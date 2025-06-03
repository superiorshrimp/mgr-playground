#!/bin/bash
#SBATCH --nodes=5
#SBATCH --ntasks-per-node=1 
#SBATCH --cpus-per-task=2   
#SBATCH --mem-per-cpu=4G    
#SBATCH -p plgrid
#SBATCH --time=00:10:00     # Max job time (e.g., 10 minutes for this test)

module load "python/3.10.4-gcccore-11.3.0"

pip install pika --quiet

mkdir -p logs
export tempdir_base="/tmp/$USER/rabbitmq_job_$SLURM_JOB_ID"
mkdir -p "$tempdir_base"
export tempdir="$tempdir_base"

nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
nodes_array=($nodes)

client_node=${nodes_array[-2]}
last_node=${nodes_array[-1]}


erlang_cookie_value=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
rabbitmq_pid_filepath="${tempdir}/rabbitmq_${last_node}.pid"

srun --overlap --nodes=1 --ntasks=1 -w "$last_node" bash -c '
  R_COOKIE_TO_WRITE=$1; REMOTE_TEMPDIR=$2; mkdir -p "$REMOTE_TEMPDIR";
  COOKIE_FILE="$HOME/.erlang.cookie";
  echo "Writing cookie $R_COOKIE_TO_WRITE to $COOKIE_FILE on $(hostname)";
  rm -f "$COOKIE_FILE"; echo "$R_COOKIE_TO_WRITE" > "$COOKIE_FILE"; chmod 400 "$COOKIE_FILE";
  echo "Cookie on $(hostname) content:"; ls -l "$COOKIE_FILE"; cat "$COOKIE_FILE";
' bash "$erlang_cookie_value" "$tempdir"

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  R_COOKIE_TO_WRITE=$1;
  COOKIE_FILE="$HOME/.erlang.cookie";
  echo "Writing cookie $R_COOKIE_TO_WRITE to $COOKIE_FILE on $(hostname) (for client ctl)";
  rm -f "$COOKIE_FILE"; echo "$R_COOKIE_TO_WRITE" > "$COOKIE_FILE"; chmod 400 "$COOKIE_FILE";
  echo "Cookie on $(hostname) content:"; ls -l "$COOKIE_FILE"; cat "$COOKIE_FILE";
' bash "$erlang_cookie_value"

srun --overlap --nodes=1 --ntasks=1 -w "$last_node" \
     -o "$server_srun_stdout_log" \
     -e "$server_srun_stderr_log" \
     bash -c '
  ARG_COOKIE_VAL=$1;
  ARG_PID_FILEPATH=$2;
  
  unset ERLANG_COOKIE; 

  export RABBITMQ_PID_FILE=$ARG_PID_FILEPATH;
  export RABBITMQ_CONSOLE_LOG=new; 

  SERVER_HOSTNAME_IN_SRUN=$(hostname)

  env ERLANG_COOKIE="$ARG_COOKIE_VAL" rabbitmq-server start
' bash "$erlang_cookie_value" "$rabbitmq_pid_filepath" &

server_srun_bg_job_pid=$!
sleep 30

if ps -p $server_srun_bg_job_pid > /dev/null; then
   echo "Main Script: Server srun task (PID $server_srun_bg_job_pid) IS still running (good)."
else
   echo "Main Script: WARNING! Server srun task $server_srun_bg_job_pid is NOT running. Server likely failed to start or exited prematurely."
   echo "Main Script: Check $server_srun_stdout_log and $server_srun_stderr_log on $last_node for details."
fi

rabbitmq_server_actual_hostname=$(srun --overlap --nodes=1 --ntasks=1 -w "$last_node" hostname)
echo "Main Script: Actual hostname for server node $last_node is $rabbitmq_server_actual_hostname"
echo "Main Script: Target for remote rabbitmqctl is rabbit@$rabbitmq_server_actual_hostname"

echo "Main Script: Step 3: Checking RabbitMQ status from $client_node (External Client srun)..."
srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" status
  echo "--- External Client srun on $CLIENT_HOSTNAME: Status SUCCESSFUL ---";
' bash "rabbit@$rabbitmq_server_actual_hostname"

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  echo "--- External Client srun on $CLIENT_HOSTNAME: Configuration ---";
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" add_user rabbitmq rabbitmq || echo "INFO: add_user rabbitmq failed, user likely already exists.";
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_user_tags rabbitmq rabbitmq;
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_permissions -p / rabbitmq ".*" ".*" ".*";
  echo "--- External Client srun on $CLIENT_HOSTNAME: Configuration Attempted ---";
' bash "rabbit@$rabbitmq_server_actual_hostname"

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  set -x
  module load "python/3.10.4-gcccore-11.3.0"
  pip install pika --quiet

  rabbitmq_node_ip=$1
  export rabbitmq_node_ip
  python3 islands_desync/geneticAlgorithm/utils/prepare_queues_2.py
' bash "$rabbitmq_server_actual_hostname"

sleep 30

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  set -x
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" list_vhosts | xargs -n1  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" list_queues -p
  sleep 30
  echo "Attempting to stop RabbitMQ server on $TARGET_RMQ_NODE_NAME_WITH_HOST from $CLIENT_HOSTNAME...";
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" stop
  echo "Stop command issued to $TARGET_RMQ_NODE_NAME_WITH_HOST from $CLIENT_HOSTNAME."
' bash "rabbit@$rabbitmq_server_actual_hostname" 
echo "Main Script: Stop command issued to server on $last_node."

echo "Main Script: Waiting for backgrounded server srun task (PID $server_srun_bg_job_pid) to complete (max 60s)..."
if ps -p $server_srun_bg_job_pid > /dev/null; then
    timeout 60s wait $server_srun_bg_job_pid || echo "WARNING: Timeout waiting for server srun PID $server_srun_bg_job_pid, or it had already exited."
else
    echo "INFO: Server srun PID $server_srun_bg_job_pid was not running before wait."
fi

echo "===== Main Sbatch Script End: $(date) ====="

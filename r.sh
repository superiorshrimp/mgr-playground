#!/bin/bash
#SBATCH --nodes=12
#SBATCH --ntasks-per-node=1 
#SBATCH --cpus-per-task=2   
#SBATCH --mem-per-cpu=4G    
#SBATCH -p plgrid

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
  rm -f "$COOKIE_FILE"; echo "$R_COOKIE_TO_WRITE" > "$COOKIE_FILE"; chmod 400 "$COOKIE_FILE";
' bash "$erlang_cookie_value" "$tempdir"

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  R_COOKIE_TO_WRITE=$1;
  COOKIE_FILE="$HOME/.erlang.cookie";
  rm -f "$COOKIE_FILE"; echo "$R_COOKIE_TO_WRITE" > "$COOKIE_FILE"; chmod 400 "$COOKIE_FILE";
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
sleep 30

server_srun_bg_job_pid=$!
rabbitmq_server_actual_hostname=$(srun --overlap --nodes=1 --ntasks=1 -w "$last_node" hostname)

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" add_user rabbitmq rabbitmq || echo "INFO: add_user rabbitmq failed, user likely already exists.";
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_user_tags rabbitmq rabbitmq;
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_permissions -p / rabbitmq ".*" ".*" ".*";
' bash "rabbit@$rabbitmq_server_actual_hostname"

sleep 5

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  module load "python/3.10.4-gcccore-11.3.0"
  pip install pika --quiet

  rabbitmq_node_ip=$1
  export rabbitmq_node_ip
  python3 islands_desync/geneticAlgorithm/utils/prepare_queues_2.py
' bash "$rabbitmq_server_actual_hostname"

sleep 30

srun --overlap --nodes=1 --ntasks=1 -w "$client_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" list_vhosts | xargs -n1  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" list_queues -p
  sleep 30
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" stop
' bash "rabbit@$rabbitmq_server_actual_hostname"


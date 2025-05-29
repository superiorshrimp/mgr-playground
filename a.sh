#!/bin/bash
#SBATCH --nodes=15
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH -p plgrid

module load "python/3.10.4-gcccore-11.3.0"

# pip install "ray[default]"
# pip install jmetalpy
# pip install scikit-learn
# pip install -r islands_desync/geneticAlgorithm/algorithm/requirements.txt
pip install pika --quiet

mkdir -p logs
export tempdir_base="/tmp/$USER/rabbitmq_job_$SLURM_JOB_ID"
mkdir -p "$tempdir_base"
export tempdir="$tempdir_base"

nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
nodes_array=($nodes)

head_node=${nodes_array[0]}
second_last_node=${nodes_array[-2]}
last_node=${nodes_array[-1]}

erlang_cookie_value=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
rabbitmq_pid_filepath="${tempdir}/rabbitmq_${last_node}.pid"

head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)
export head_node_ip

srun --overlap --nodes=1 --ntasks=1 -w "$last_node" bash -c '
  R_COOKIE_TO_WRITE=$1; REMOTE_TEMPDIR=$2; mkdir -p "$REMOTE_TEMPDIR";
  COOKIE_FILE="$HOME/.erlang.cookie";
  rm -f "$COOKIE_FILE"; echo "$R_COOKIE_TO_WRITE" > "$COOKIE_FILE"; chmod 400 "$COOKIE_FILE";
' bash "$erlang_cookie_value" "$tempdir"

srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
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

rabbitmq_node_ip="$rabbitmq_server_actual_hostname"
export rabbitmq_node_ip

srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" add_user rabbitmq rabbitmq || echo "INFO: add_user rabbitmq failed, user likely already exists.";
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_user_tags rabbitmq rabbitmq;
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_permissions -p / rabbitmq ".*" ".*" ".*";
' bash "rabbit@$rabbitmq_server_actual_hostname"

sleep 5

srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
  module load "python/3.10.4-gcccore-11.3.0"
  pip install pika --quiet

  rabbitmq_node_ip=$1
  export rabbitmq_node_ip
  python3 islands_desync/geneticAlgorithm/utils/prepare_queues_2.py
' bash "$rabbitmq_server_actual_hostname"

port=6379
ip_head=$head_node_ip:$port
export ip_head

ray stop
export RAY_DEDUP_LOGS=0
echo "Starting HEAD at $head_node"
srun --nodes=1 --ntasks=1 -w "$head_node" \
    ray start --head --node-ip-address="$head_node_ip" --port=$port \
    --num-cpus "${SLURM_CPUS_PER_TASK}" --temp-dir="/tmp/$USER" --block &
sleep 1

islands_count=10
migrants_count=2
migration_interval=16
blocking=0

for ((i = 1; i <= islands_count; i++)); do
    node_i=${nodes_array[$i]}
    echo "Starting WORKER $i at $node_i"
    srun --nodes=1 --ntasks=1 -w "$node_i" --export=ALL \
        ray start --address "$ip_head" --num-cpus "${SLURM_CPUS_PER_TASK}" --block &
    sleep 1
done

python -u islands_desync/minimal.py $islands_count $migrants_count $migration_interval RingTopology MinStdDevSelect $blocking

ray stop

sleep 30

srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" stop
' bash "rabbit@$rabbitmq_server_actual_hostname"


#!/bin/bash
#SBATCH --nodes=27
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
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

srun --overlap --nodes=1 --ntasks=1 -w "$last_node" bash -c '
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
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" set_user_tags rabbitmq administrator;
  rabbitmq-plugins -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" enable rabbitmq_management
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
sleep 5
export RAY_DEDUP_LOGS=0
echo "Starting HEAD at $head_node"
srun --nodes=1 --ntasks=1 -w "$head_node" \
    ray start --head --node-ip-address="$head_node_ip" --port=$port \
    --num-cpus "${SLURM_CPUS_PER_TASK}" --temp-dir="/tmp/$USER" --block &
sleep 1

islands_count=25
migrants_count=2
migration_interval=64
blocking=0

for ((i = 1; i <= islands_count; i++)); do
    node_i=${nodes_array[$i]}
    echo "Starting WORKER $i at $node_i"
    srun --nodes=1 --ntasks=1 -w "$node_i" --export=ALL \
        ray start --address "$ip_head" --num-cpus "${SLURM_CPUS_PER_TASK}" --block &
    sleep 1
done

METRICS_COLLECTION_DURATION=35
METRICS_INTERVAL=1
metrics_overview_data_file_on_client="logs/metrics_overview_data_${last_node}_${SLURM_JOB_ID}.json"
metrics_queues_data_file_on_client="logs/metrics_queues_data_${last_node}_${SLURM_JOB_ID}.json"
srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
  SERVER_IP_FOR_API=$1;
  OVERVIEW_DATA_LOG_PATH=$2;
  QUEUES_DATA_LOG_PATH=$3;
  DURATION=$4;
  INTERVAL=$5;

  mkdir -p "$(dirname "$OVERVIEW_DATA_LOG_PATH")";

  end_time=$(( $(date +%s) + DURATION ));
  iteration=0;
  while [ $(date +%s) -lt $end_time ]; do
    iteration=$((iteration + 1));
    current_timestamp_for_log_entry=$(date +"%Y-%m-%d %H:%M:%S.%3N") # For prepending to JSON data

    if curl -s -f -u rabbitmq:rabbitmq "http://${SERVER_IP_FOR_API}:15672/api/overview" >> "$OVERVIEW_DATA_LOG_PATH"; then
        echo "" >> "$OVERVIEW_DATA_LOG_PATH";
    else
        echo "ERROR: curl to /api/overview failed for iteration $iteration at $current_timestamp_for_log_entry" >> "$OVERVIEW_DATA_LOG_PATH";
    fi

    if curl -s -f -u rabbitmq:rabbitmq "http://${SERVER_IP_FOR_API}:15672/api/queues" >> "$QUEUES_DATA_LOG_PATH"; then
        echo "" >> "$QUEUES_DATA_LOG_PATH";
    else
        echo "ERROR: curl to /api/queues failed for iteration $iteration at $current_timestamp_for_log_entry" >> "$QUEUES_DATA_LOG_PATH";
    fi

    if ! ps -p $$ > /dev/null; then
        echo "Metrics Collector: Parent shell (PID $$) gone, exiting loop."
        break
    fi

    sleep "$INTERVAL";
  done
  echo "Metrics Collector on $(hostname): Finished. Total iterations: $iteration";
' bash "$rabbitmq_node_ip" "$metrics_overview_data_file_on_client" "$metrics_queues_data_file_on_client" "$METRICS_COLLECTION_DURATION" "$METRICS_INTERVAL" &

python -u islands_desync/minimal.py $islands_count $migrants_count $migration_interval CompleteTopology MinStdDevSelect $blocking

ray stop

sleep 30

srun --overlap --nodes=1 --ntasks=1 -w "$second_last_node" bash -c '
  TARGET_RMQ_NODE_NAME_WITH_HOST=$1
  CLIENT_HOSTNAME=$(hostname)
  rabbitmqctl -n "$TARGET_RMQ_NODE_NAME_WITH_HOST" stop
' bash "rabbit@$rabbitmq_server_actual_hostname"

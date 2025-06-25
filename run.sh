#!/bin/bash
#SBATCH --nodes=12
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4G
#SBATCH -p plgrid

module load "python/3.10.4-gcccore-11.3.0"

# pip install "ray[default]"
# pip install jmetalpy
# pip install scikit-learn
pip install pika
# pip install -r islands_desync/geneticAlgorithm/algorithm/requirements.txt

mkdir -p logs
export tempdir=/tmp/$USER
mkdir -p $tempdir

nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
nodes_array=($nodes)

head_node=${nodes_array[0]}
last_node=${nodes_array[-1]}

head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)
rabbitmq_node_ip=$(srun --nodes=1 --ntasks=1 -w "$last_node" hostname --ip-address)

# --- RabbitMQ Specific Setup ---
# Get the short hostname for the RabbitMQ node
rabbitmq_short_hostname=$(srun --nodes=1 --ntasks=1 -w "$last_node" hostname -s)
# Generate a random cookie for this job
export RMQ_COOKIE=$(cat /dev/urandom | tr -dc 'A-Z0-9' | fold -w 32 | head -n 1)
# Define the nodename
export RMQ_NODENAME="rabbit@$rabbitmq_short_hostname"

echo "RabbitMQ Node: $last_node ($rabbitmq_node_ip)"
echo "RabbitMQ Short Hostname: $rabbitmq_short_hostname"
echo "RabbitMQ Nodename: $RMQ_NODENAME"

export head_node_ip
export rabbitmq_node_ip

# --- Start RabbitMQ ---
echo "Starting RabbitMQ Server at $last_node..."
# Export the cookie and nodename *within* the srun command
# Ensure RabbitMQ uses these specific settings.
srun --nodes=1 --ntasks=1 -w "$last_node" --export=ALL \
    bash -c '
        export RABBITMQ_NODENAME='"$RMQ_NODENAME"'
        export RABBITMQ_ERLANG_COOKIE='"$RMQ_COOKIE"'
        rabbitmq-server > "'"$tempdir"'/rabbitmq_'"$last_node"'.log" 2>&1
    ' &

echo "Giving RabbitMQ time to initialize (25 seconds)..."
sleep 25

# --- Check EPMD (Diagnostics) ---
echo "Checking EPMD on $last_node..."
srun --nodes=1 --ntasks=1 -w "$last_node" epmd -names || echo "WARN: Could not query EPMD."

# --- Configure RabbitMQ ---
echo "Waiting for RabbitMQ startup to complete (60s timeout)..."
# Use bash -c again to ensure environment variables are set for rabbitmqctl
srun --nodes=1 --ntasks=1 -w "$last_node" --export=ALL \
    bash -c '
        export RABBITMQ_NODENAME='"$RMQ_NODENAME"'
        export RABBITMQ_ERLANG_COOKIE='"$RMQ_COOKIE"'
        rabbitmqctl --timeout 60 await_startup
    ' || { echo "ERROR: RabbitMQ await_startup failed or timed out. Check $tempdir/rabbitmq_$last_node.log"; exit 1; }

echo "Configuring RabbitMQ user and permissions..."
srun --nodes=1 --ntasks=1 -w "$last_node" --export=ALL \
    bash -c '
        export RABBITMQ_NODENAME='"$RMQ_NODENAME"'
        export RABBITMQ_ERLANG_COOKIE='"$RMQ_COOKIE"'
        rabbitmqctl add_user rabbitmq rabbitmq || echo "WARN: Could not add user (maybe exists?)"
        rabbitmqctl set_user_tags rabbitmq rabbitmq
        rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
    '

echo "Preparing RabbitMQ queues..."
srun --nodes=1 --ntasks=1 -w "$last_node" --export=ALL \
    bash -c '
        export RABBITMQ_NODENAME='"$RMQ_NODENAME"'
        export RABBITMQ_ERLANG_COOKIE='"$RMQ_COOKIE"'
        python3 islands_desync/geneticAlgorithm/utils/prepare_queues_2.py
    ' || { echo "ERROR: Python queue preparation failed."; exit 1; }

echo "Listing queues..."
srun --nodes=1 --ntasks=1 -w "$last_node" --export=ALL \
    bash -c '
        export RABBITMQ_NODENAME='"$RMQ_NODENAME"'
        export RABBITMQ_ERLANG_COOKIE='"$RMQ_COOKIE"'
        rabbitmqctl list_vhosts | xargs -I {} rabbitmqctl list_queues --vhost {} name messages
    '
port=6379
ip_head=$head_node_ip:$port
export ip_head
echo "IP Head: $ip_head"

ray stop
export RAY_DEDUP_LOGS=0
echo "Starting HEAD at $head_node"
srun --nodes=1 --ntasks=1 -w "$head_node" \
    ray start --head --node-ip-address="$head_node_ip" --port=$port \
    --num-cpus "${SLURM_CPUS_PER_TASK}" --temp-dir="$tempdir" --block &
sleep 1

worker_num=$((SLURM_JOB_NUM_NODES - 2))
for ((i = 1; i <= worker_num; i++)); do
    node_i=${nodes_array[$i]}
    echo "Starting WORKER $i at $node_i"
    srun --nodes=1 --ntasks=1 -w "$node_i" --export=ALL,RAY_TMPDIR="$tmpdir",rabbitmq_node_ip="$rabbitmq_node_ip"\
        ray start --address "$ip_head" --num-cpus "${SLURM_CPUS_PER_TASK}" --block &
    sleep 1
done

sleep 10

islands_count=10
migrants_count=2
migration_interval=16
blocking=0

python -u islands_desync/minimal.py $islands_count $migrants_count $migration_interval RingTopology MinStdDevSelect $blocking

ray stop

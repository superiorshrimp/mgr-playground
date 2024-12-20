#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2G
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

rabbitmq-server start -detached

# Getting the node names
nodes=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
nodes_array=($nodes)

head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)
export head_node_ip

# Start ray head
port=6379
ip_head=$head_node_ip:$port
export ip_head
echo "IP Head: $ip_head"

echo "Starting HEAD at $head_node"
srun --nodes=1 --ntasks=1 -w "$head_node" \
    ray start --head --node-ip-address="$head_node_ip" --port=$port \
    --num-cpus "${SLURM_CPUS_PER_TASK}" --temp-dir="$tempdir" --block &
sleep 1

# Start ray workers
worker_num=$((SLURM_JOB_NUM_NODES - 1))
for ((i = 1; i <= worker_num; i++)); do
    node_i=${nodes_array[$i]}
    echo "Starting WORKER $i at $node_i"
    srun --nodes=1 --ntasks=1 -w "$node_i" --export=ALL,RAY_TMPDIR="$tmpdir"\
        ray start --address "$ip_head" --num-cpus "${SLURM_CPUS_PER_TASK}" --block &
    # sleep 1
done

sleep 1

python3 islands_desync/geneticAlgorithm/utils/prepare_queues_2.py

rabbitmqctl list_vhosts | xargs -n1  rabbitmqctl list_queues -p

islands_count=3
migrants_count=2
migration_interval=16

python -u islands_desync/minimal.py $islands_count $migrants_count $migration_interval RingTopology MaxDistanceSelect

ray stop


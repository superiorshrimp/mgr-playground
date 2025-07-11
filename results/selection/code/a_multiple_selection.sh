export islands=25
export blocking=0

#declare -a arr=("0.0" "0.05" "0.1" "0.15" "0.2" "0.25" "0.3" "0.35" "0.4" "0.45" "0.5" "0.55" "0.6" "0.65" "0.7" "0.75" "0.8" "0.85" "0.9" "0.95" "1.0")
declare -a arr=("0.80" "0.82" "0.84" "0.86" "0.88" "0.90" "0.92" "0.94" "0.96" "0.98" "1.00")
#declare -a arr=("0.9" "0.95" "1.0")
#declare -a arr=("0.75" "0.80" "0.85" "0.90" "0.95" "1.0")
#declare -a arr=("1.0")

for delay in {10..10..5}; do
  for coef in "${arr[@]}"; do
    echo "Running script.py with delay=$delay"
    python3 islands_desync/desync_config.py "$islands" "$delay" "complete" "$coef"

    jobid=$(sbatch --output=slurm-c${coef}d${delay}-0 a.sh | awk '{print $4}')

    for i in {1..2..1}; do
        echo "Waiting for job $jobid to finish (timeout: a lot of mins)"
        timeout=5000
        waited=0
        while squeue -j "$jobid" 2>/dev/null | grep -q "$jobid"; do
            sleep 5
            waited=$((waited + 5))
            if [ "$waited" -ge "$timeout" ]; then
                echo "Timeout waiting for job $jobid after 10 minutes. Continuing..."
                break
            fi
        done

        jobid=$(sbatch --output=slurm-c${coef}d${delay}-${i} a.sh | awk '{print $4}')

        rm -fr ../rabbitmq_server-4.0.5/var/log/rabbitmq/*
        rm -fr ../rabbitmq_server-4.0.5/var/lib/rabbitmq/mnesia/*
    done

    echo "Waiting for final job $jobid to finish before next delay (timeout: a lot of mins)"
    timeout=5000
    waited=0
    while squeue -j "$jobid" 2>/dev/null | grep -q "$jobid"; do
        sleep 5
        waited=$((waited + 5))
        if [ "$waited" -ge "$timeout" ]; then
            echo "Timeout waiting for job $jobid after 10 minutes. Continuing..."
            break
        fi
    done
  done
done

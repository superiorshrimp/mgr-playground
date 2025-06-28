export islands=25
export blocking=1

for delay in {5..10..5}; do
    echo "Running script.py with delay=$delay"
    python3 islands_desync/desync_config.py "$islands" "$delay"

    jobid=$(sbatch --output=slurm-b${blocking}d${delay}-0 a.sh | awk '{print $4}')

    for i in {1..3}; do
        echo "Waiting for job $jobid to finish (timeout: 10 mins)"
        timeout=3000
        waited=0
        while squeue -j "$jobid" 2>/dev/null | grep -q "$jobid"; do
            sleep 5
            waited=$((waited + 5))
            if [ "$waited" -ge "$timeout" ]; then
                echo "Timeout waiting for job $jobid after 10 minutes. Continuing..."
                break
            fi
        done

        jobid=$(sbatch --output=slurm-b${blocking}d${delay}-${i} a.sh | awk '{print $4}')

        rm -fr ../rabbitmq_server-4.0.5/var/log/rabbitmq/*
        rm -fr ../rabbitmq_server-4.0.5/var/lib/rabbitmq/mnesia/*
    done

    echo "Waiting for final job $jobid to finish before next delay (timeout: 10 mins)"
    timeout=3000
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

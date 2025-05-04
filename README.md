# mgr-playground

### Instalacja

lokalnie:
```
pip install "ray[default]"
pip install pika

ray start --head --port=6379 --dashboard-port=6380

docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
python islands_desync/geneticAlgorithm/utils/prepare_queues_2.py 

rabbitmqctl await_startup
rabbitmqctl add_user rabbitmq rabbitmq
rabbitmqctl set_user_tags rabbitmq rabbitmq
rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"

# example run:
python islands_desync\minimal.py 3 4 8 CompleteTopology RandomSelect 1

ray stop
```

AWS EC2:
```
sudo yum update
sudo -y yum install docker
sudo usermod -a -G docker ec2-user
id ec2-user
newgrp docker
sudo systemctl enable docker.service
sudo systemctl start docker.service
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Cyfronet:
```
# set ip of rabbitmq deployment
sbatch run.sh
```
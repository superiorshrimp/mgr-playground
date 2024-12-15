import json

import pika

conf_file = "islands_desync/geneticAlgorithm/algorithm/configurations/algorithm_configuration.json"

connection = pika.BlockingConnection(pika.ConnectionParameters(host="3.89.61.251"))
channel = connection.channel()
delay_channel = connection.channel()


with open(conf_file) as file:
    configuration = json.loads(file.read())

rabbitmq_delays = configuration["island_delays"]
number_of_islands = 3

def remove_queues():
    for island in range(number_of_islands):
        channel.queue_delete(queue=f"island-{island}")
        for i in range(number_of_islands):
            channel.queue_delete(f"island-from-{island}-to-{i}")

def create_queues():
    for island in range(number_of_islands):
        queue_name = f"island-{island}"
        channel.queue_declare(queue=queue_name)
        for i in range(number_of_islands):
            if i != island:
                if rabbitmq_delays[str(island)][i] == -1:
                    continue
                try:
                    delay_channel.queue_declare(
                        queue=f"island-from-{island}-to-{i}",
                        arguments={
                            "x-message-ttl": int(rabbitmq_delays[str(island)][i]),  # Delay until the message is transferred in milliseconds.
                            "x-dead-letter-exchange": "amq.direct",  # Exchange used to transfer the message from A to B.
                            "x-dead-letter-routing-key": f"island-{i}",  # Name of the queue we want the message transferred to.
                        },
                    )
                except IndexError as e:
                    print("Create queues failed")
                    print(f"Invalid island delays configuration: {e}")
                    print(
                        f" Number of islands is {number_of_islands}, island 1 index: {island}, island 2 index: {i}"
                    )
                    exit(1)

    connection.close()


remove_queues()
create_queues()

# docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

import json
import random
from ..emas.Agent import Agent
from ..emas.Problem import Rastrigin
import pika
import datetime
from islands.core.Migration import Migration


class QueueMigration(Migration):
    def __init__(self, island, channel, rabbitmq_delays, number_of_islands):
        super().__init__()
        self.island = island
        self.channel = channel
        self.rabbitmq_delays = rabbitmq_delays
        self.number_of_islands = number_of_islands

    def migrate_individuals(
        self, individuals_to_migrate, iteration_number, island_number, timestamp, island
    ):
        for i in individuals_to_migrate:
            destination = random.choice(
                [
                    i
                    for i in range(self.number_of_islands)
                    if i != self.island
                    and self.rabbitmq_delays[str(self.island)][i] != -1
                ]
            )
            # print(self.recursive_dict(i))
            data = self.recursive_dict(i)
            data["timestamp"] = datetime.datetime.now().timestamp()
            data["source_island"] = self.island
            self.channel.basic_publish(
                exchange="amq.direct",
                routing_key=f"island-from-{self.island}-to-{destination}",
                body=json.dumps(data), # i.__dict__
            )

    def receive_individuals(
        self, step_num: int, evaluations: int
    ) :
        new_individuals = []
        emigration_at_step_num = None
        for i in range(self.number_of_islands):
            method, properties, body = self.channel.basic_get(f"island-{self.island}")
            if body:
                data_str = body.decode("utf-8")
                data = json.loads(data_str)
                new_agent = Agent(
                    data['x'],
                    100, # start_energy
                    Rastrigin(data['problem']['n_dim'], data['problem']['a']),
                    data['lower_bound'],
                    data['upper_bound']
                )
                new_individuals.append(new_agent)

                emigration_at_step_num = {
                    "step": step_num,
                    "ev": evaluations,
                    "iteration_numbers": 1, # TODO
                    "timestamps": data['timestamp'],
                    "src_islands": data['source_island'],
                    "fitnesses": new_agent.fitness,
                } # TODO: emigration at step should maybe be a list?

        return new_individuals, emigration_at_step_num

    def recursive_dict(self, obj):
        if hasattr(obj, '__dict__'):
            return {key: self.recursive_dict(value) for key, value in obj.__dict__.items()}
        return obj
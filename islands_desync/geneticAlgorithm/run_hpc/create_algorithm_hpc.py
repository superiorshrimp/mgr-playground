import json

import ray

from ..emas.Problem import Rastrigin

from geneticAlgorithm.algorithm.emas_genetic_island_algorithm import GeneticIslandAlgorithm
from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.core.Emigration import Emigration
from geneticAlgorithm.utils.create_rabbitmq_channels import CreateRabbitmqChannels
from geneticAlgorithm.migrations.queue_migration import QueueMigration


def emas_create_algorithm_hpc(island: ray.ObjectRef, island_id: int, migration: Emigration, params: RunAlgorithmParams) -> GeneticIslandAlgorithm:
    conf_file = "./islands_desync/geneticAlgorithm/algorithm/configurations/algorithm_configuration.json"
    with open(conf_file) as file: configuration = json.loads(file.read())

    NUMBER_OF_VARIABLES = int(configuration["number_of_variables"])
    NUMBER_OF_EVALUATIONS = int(configuration["number_of_evaluations"])
    POPULATION_SIZE = int(configuration["population_size"])
    OFFSPRING_POPULATION_SIZE = int(configuration["offspring_population_size"])

    problem = Rastrigin(NUMBER_OF_VARIABLES)

    migration = create_delays(configuration, NUMBER_OF_EVALUATIONS, island_id) # TODO: revert if want delays

    genetic_island_algorithm = GeneticIslandAlgorithm(
        problem=problem,
        evaluations=NUMBER_OF_EVALUATIONS,
        population_size=POPULATION_SIZE,
        offspring_population_size=OFFSPRING_POPULATION_SIZE,
        migration_interval=params.migration_interval,
        number_of_islands=params.island_count,
        number_of_emigrants=params.number_of_emigrants,
        island=island_id,
        island_ref=island,
        want_run_end_communications=configuration["want_run_end_communications"],
        type_of_connection=configuration["type_of_connection"],
        migrant_selection_type=configuration["migrant_selection_type"],
        how_many_data_intervals=configuration["how_many_data_intervals"],
        plot_population_interval=configuration["plot_population_interval"],
        par_date=params.dda,
        par_time=params.tta,
        wyspWRun=params.island_count,
        seria=params.series_number,
        migration=migration,
    )

    return genetic_island_algorithm

def create_delays(configuration, NUMBER_OF_EVALUATIONS, island_id):
    rabbitmq_delays = configuration["island_delays"]

    channel = CreateRabbitmqChannels(
        3,
        island_id,
        data_interval=round(
            NUMBER_OF_EVALUATIONS // 50 #configuration["how_many_data_intervals"]
        ),
        max_evaluations=NUMBER_OF_EVALUATIONS,
        rabbitmq_delays=rabbitmq_delays,
    ).create_channels()
    migration = QueueMigration(
        island_id,
        channel=channel,
        number_of_islands=3,
        rabbitmq_delays=rabbitmq_delays,
    )

    return migration
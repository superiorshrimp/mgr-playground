import json
import os
import random
from time import time
from typing import List, TypeVar
import ray
from math import inf

import numpy as np
from ..emas.Problem import Problem

from islands.core.Migration import Migration
from ..utils import (
    controller,
    datetimer,
    distance,
    filename,
)

S = TypeVar("S")
R = TypeVar("R")

from matplotlib import pyplot as plt

from ..emas.EMAS import EMAS
from ..emas.Config import Config

class GeneticIslandAlgorithm:
    def __init__(
        self,
        problem: Problem,
        evaluations: int,
        population_size: int,
        offspring_population_size: int,
        migration_interval: int,
        number_of_islands: int,
        number_of_emigrants: int,
        island: int,
        island_ref: ray.ObjectRef,
        want_run_end_communications: str,
        type_of_connection: str,
        migrant_selection_type: str,
        how_many_data_intervals: int,
        plot_population_interval: int,
        par_date: str,
        par_time: str,
        wyspWRun: int,
        seria: int,
        migration: Migration,
    ):
        self.population_size = population_size
        self.offspring_population_size = offspring_population_size
        self.max_evaluation = evaluations
        self.n_iter=evaluations // self.offspring_population_size # for compatibility with main
        config = Config(
            problem=problem,
            n_agent=population_size,
            n_iter=evaluations // self.offspring_population_size, # for compatibility with main
            lower_bound=-5.12,
            upper_bound=5.12,
            start_energy=100,
            reproduce_energy=150,
            alive_energy=1,
            energy_reproduce_loss_coef=0.2,
            energy_fight_loss_coef=0.8,
            energy_diff_loss_coef=0.8,
            cross_coef=0.55,
            mutation_coef=0.02,
        )
        self.emas = EMAS(config)
        self.solutions = self.emas.agents
        self.evaluations = 0

        self.problem = problem
        self.migration = migration
        self.min_fitness_per_evaluation = dict()
        self.migration_interval = migration_interval
        self.number_of_emigrants = number_of_emigrants
        self.number_of_islands = number_of_islands
        self.island = island
        self.island_ref = island_ref
        self.want_run_end_communications = want_run_end_communications
        self.last_migration_evaluation_number = 0

        self.type_of_connection = type_of_connection
        self.migrant_selection_type = migrant_selection_type
        self.how_many_data_intervals = how_many_data_intervals

        self.plot_population_interval = plot_population_interval
        self.par_date = par_date
        self.par_time = par_time
        self.wyspWRun = wyspWRun
        self.seria = (seria,)
        (seriaa,) = self.seria
        self.seria = seriaa
        self.tab_emigr = {}

        self.ts1 = time()

        self.dta = datetimer.Datetimer(self, self.want_run_end_communications)
        self.czasStart = self.dta.teraz()
        self.dist = distance.Distance()

        # SCIEZKA I NAZWA PLIKOW
        self.fileName = filename.Filename(self, self.want_run_end_communications)
        if (
            self.problem.name()[0:4] == "Labs"
        ):  # <----       todo: LABS i problemy gdzie szukamy max
            self.Fname = self.fileName.getname(
                par_date + "_" + par_time,
                self.problem.name()[0:4],
                self.problem.number_of_variables(),
                "",
                self.island,
                self.number_of_islands,
                self.population_size,
                self.offspring_population_size,
                self.termination_criterion.max_evaluations,
            )
        else:
            self.Fname = self.fileName.getname(
                par_date + "_" + par_time,
                self.problem.name()[0:4],
                self.problem.n_dim,
                "",
                self.island,
                self.number_of_islands,
                self.population_size,
                self.offspring_population_size,
                self.n_iter,
            )

        self.path = self.fileName.getpath(
            self.par_date,
            self.problem.name()[0:4],
            self.problem.n_dim,
            self.par_time,
            self.number_of_islands,
            self.migrant_selection_type[0],
            "k",
            self.migration_interval,
            self.number_of_emigrants,
        )
        self.fullPath = self.path + "/" + self.Fname

        #KATALOG NA REZULTATY
        if self.island == 0:
            os.makedirs(self.path, exist_ok=True)
            if self.want_run_end_communications:
                print(
                    "\n\n\n                          The new directory is created! by island: "
                    + str(self.island)
                    + "\n\n\n"
                )

        # self.ctrl = controller.Controller(
        #     self.path, self.island, self.want_run_end_communications
        # ) # kontrolW0Start.ctrl.txt / kontrolW0End.ctrl.txt
        self.step_num = 0
        self.last_best = inf

        self.is_new_immigrant = False
        self.bylLog = False

    def __str__(self):
        return "emas_genetic_island_algorithm"

    def __del__(self):
        if self.want_run_end_communications:
            print("koniec emas_genetic_island_algorithm")

    def run(self):
        start = time()
        it = 0
        while self.evaluations < self.max_evaluation:
            it += 1
            self.step()
        # for i in range(self.n_iter):
        #     it += 1
        #     self.step()
        print("time:", time() - start)
        print(sorted(self.solutions, key=lambda agent: agent.fitness)[0].fitness)
        # self.plot_history(it)
        # self.save_history()
        self.save_history_short()
        json.dump(self.tab_emigr, open("history/w"+str(self.island)+".json", "w"), indent=4)

    def save_history_short(self):
        dir = "history/"
        os.makedirs(dir, exist_ok=True)
        with open(dir + self.par_time + ".json", "a") as f:
            f.write(str(self.island) + " " + str(self.emas.best_fit[-1]) + "\n")
        with open(dir + "t.txt", "a") as f:
            f.write(str(self.island) + " " + str(self.migration.start) + " " + str(self.migration.end) + "\n")

    # def save_history(self):
    #     dir = "history/" + self.par_date + "/"
    #     os.makedirs(dir, exist_ok=True)
    #     dir += self.par_time + "/"
    #     os.makedirs(dir, exist_ok=True)
    #     with open(dir + str(self.island) + ".json", "w") as f:
    #         json.dump({
    #             "variance": self.emas.variance,
    #             "fitness": self.emas.best_fit,
    #         }, f)

    def plot_history(self, it):
        iter = [i for i in range(it + 1)]

        plt.plot(iter, self.emas.variance)
        avg_windows_size = 100
        plt.plot(iter[avg_windows_size:], [np.mean(self.emas.variance[i:i+avg_windows_size]) for i in range(len(iter)-avg_windows_size)])
        plt.xticks(iter[avg_windows_size::100], rotation=45)
        plt.ylim([0, 2])
        plt.xlabel('iteration')
        plt.savefig("dev" + str(self.island) + '.png')
        plt.clf()

        plt.plot(iter, self.emas.best_fit)
        plt.xticks(iter[::100], rotation=45)
        plt.ylim([0, 100])
        plt.xlabel('iteration')
        plt.savefig("fit" + str(self.island) + '.png')
        plt.clf()

        plt.plot(iter, self.emas.alive_count)
        plt.xlabel('iteration')
        plt.xticks(rotation=45)
        plt.savefig("liv" + str(self.island) + '.png')

    def get_result(self):
        return sorted(self.solutions, key=lambda agent: agent.fitness)[0]

    # MIGRATION SECTION  -----------------------------------------------------------
    def get_individuals_to_migrate(self, population: List[S], number_of_emigrants: int) -> List[S]:
        if len(population) < number_of_emigrants:
            raise ValueError("Population is too small")

        match self.migrant_selection_type:
            case 'random':
                emigrants = [
                    population[random.randrange(len(population))]
                    for _ in range(0, number_of_emigrants)
                ]
            case 'maxDistance':
                emigrants_num = self.dist.maxDistanceTab(
                    population, self.number_of_emigrants
                )
                emigrants = [population[i] for i in emigrants_num]
            case 'best':
                emigrants_num = self.dist.bestTab(population, self.number_of_emigrants)
                emigrants = [population[i] for i in emigrants_num]
            case 'worst':
                emigrants_num = self.dist.worstTab(population, self.number_of_emigrants)
                emigrants = [population[i] for i in emigrants_num]
            case _:
                raise ValueError("WRONG MIGRANT SELECTION METHOD")

        return emigrants

    def migrate_individuals(self):
        if self.evaluations - self.last_migration_evaluation_number >= self.migration_interval:
            try:
                individuals_to_migrate = self.get_individuals_to_migrate(
                    self.solutions, self.number_of_emigrants
                )
                self.last_migration_evaluation_number = self.evaluations
            except ValueError as ve:
                print("-- ValueError -- migrate individuals  --", ve.__str__(), " ", self.island, " ", self.step_num)
                return

            self.migration.migrate_individuals(
                individuals_to_migrate, self.step_num, self.island, time(), self.island
            )

    def add_new_individuals(self):
        new_individuals, emigration_at_step_num = self.migration.receive_individuals(
            self.step_num, self.evaluations
        )

        # for i in new_individuals:
        #     i.energy = 0

        if len(new_individuals) > 0:
            print("bbb " + str(len(new_individuals)) + " " + str(self.island))
            print("ccc" + str(self.island))
            print("ddd " + str(type(new_individuals)) + " " + str(new_individuals[0]))
            self.is_new_immigrant = True
            emigration_at_step_num["destinTimestamp"] = time()
            emigration_at_step_num["destinMaxFitness"] = self.last_best
            self.tab_emigr[self.step_num] = emigration_at_step_num
            self.solutions.extend(list(new_individuals))

    def step(self):
        self.step_num += 1
        if self.step_num == 1:
            # self.migration.wait_for_all_start()
            self.migration.start_time_measure()

        # MIGRATIONS
        self.is_new_immigrant = False
        if self.number_of_islands > 1:
            self.migrate_individuals()
            try:
                self.add_new_individuals()
            except: pass # TODO: why throws?

        # EVOLUTIONARY STEP
        self.emas.agents = self.solutions
        children_count = self.emas.iteration(self.step_num)
        
        self.log_history()

        self.solutions = self.emas.agents
        self.solutions.sort(key=lambda agent: agent.fitness)
        self.last_best = min(self.solutions[0].fitness, self.last_best)

        if self.step_num % 5 == 0:
            self.migration.end_time_measure()
            self.last_best = self.solutions[0].fitness
            # self.ctrl.endOfProcess(self.island, self.last_best) # kontrolW0Start.ctrl.txt / kontrolW0End.ctrl.txt

            # self.migration.signal_finish()

            # if self.island == 0:
            #     self.migration.wait_for_finish()
            #     self.ctrl.endOfWholeProbe(self.seria)
        
        self.evaluations += children_count

    def update_island_data(self):
        self.island_ref.set_population.remote(self.emas.agents)
        self.island_ref.set_fitness.remote(self.last_best)
        std_dev = np.sum(np.std([agent.x for agent in self.emas.agents], axis=1))
        self.island_ref.set_std_dev.remote(std_dev)

    def log_history(self):
        self.emas.alive_count.append(len(self.emas.agents))
        self.emas.energy_data_sum.append(sum([i.energy for i in self.emas.agents]))
        self.emas.energy_data_avg.append(sum([i.energy for i in self.emas.agents]) / len(self.emas.agents))
        self.emas.best_fit.append(min(self.emas.agents, key=lambda a: a.fitness).fitness)
        self.emas.variance.append(sum(np.var([i.x for i in self.emas.agents], axis=0)))

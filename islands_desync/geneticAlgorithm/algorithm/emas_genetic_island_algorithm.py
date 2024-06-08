import json
import os
import random
import statistics
from copy import deepcopy
import time
from datetime import datetime
from math import trunc
from typing import List, TypeVar

import numpy as np
import pandas as pd
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.config import store
from jmetal.core.operator import Crossover, Mutation, Selection
from ..emas.Problem import Problem
from jmetal.util.evaluator import Evaluator
from jmetal.util.generator import Generator
from jmetal.util.termination_criterion import TerminationCriterion

from islands.core.Migration import Migration
from ..solution.float_island_solution import FloatIslandSolution
from ..utils import (
    boxPloter,
    controller,
    datetimer,
    distance,
    filename,
    fileslister,
    logger,
    ploter,
    result_saver,
    tsne,
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
        population_size: int,
        offspring_population_size: int,
        migration_interval: int,
        number_of_islands: int,
        number_of_emigrants: int,
        island: int,
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
        config = Config(
            problem=problem,
            n_agent=population_size,
            n_iter=1000,
            lower_bound=-5.12,
            upper_bound=5.12,
            start_energy=100,
            reproduce_energy=150,
            alive_energy=2,
            energy_reproduce_loss_coef=0.1,
            energy_fight_loss_coef=0.2,
            cross_coef=0.55,
            mutation_coef=0.05,
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
        self.want_run_end_communications = want_run_end_communications
        self.last_migration_evolution = 0

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

        self.ts1 = time.time()

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
                1000, # TODO: param max eval
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
            os.makedirs(self.path)
            if self.want_run_end_communications:
                print(
                    "\n\n\n                          The new directory is created! by island: "
                    + str(self.island)
                    + "\n\n\n"
                )

        self.ctrl = controller.Controller(
            self.path, self.island, self.want_run_end_communications
        )
        self.step_num = 0
        self.lastBest = 50000.0

        self.nowi = False
        self.bylLog = False

    def __str__(self):
        return "genetic_island_algorithm"

    def __del__(self):
        if self.want_run_end_communications:
            print("koniec genetic_island_algorithm")

    def run(self):
        for i in range(1000):
            self.step()
        print(sorted(self.solutions,key=lambda agent: agent.fitness)[0].fitness)
        iter = [i for i in range(self.emas.config.n_iter + 1)]
        plt.plot(iter, self.emas.alive_count)
        plt.plot(iter, self.emas.variance)
        plt.plot(iter, self.emas.best_fit)
        plt.savefig(str(self.island) + '.png')


    def get_result(self):
        return sorted(self.solutions, key=lambda agent: agent.fitness)[0]

    # MIGRATION SECTION  -----------------------------------------------------------
    def get_individuals_to_migrate(
        self, population: List[S], number_of_emigrants: int
    ) -> List[S]:
        if len(population) < number_of_emigrants:
            raise ValueError("Population is too small")

        # "random", "maxDistance", "best", "worst"
        if self.migrant_selection_type == "maxDistance":
            emigrantsnum = self.dist.maxDistanceTab(
                population, self.number_of_emigrants
            )
            emigrants = [population[i] for i in emigrantsnum]
        elif self.migrant_selection_type == "best":
            emigrantsnum = self.dist.bestTab(population, self.number_of_emigrants)
            emigrants = [population[i] for i in emigrantsnum]
        elif self.migrant_selection_type == "worst":
            # if self.step_num<100:
            #    print("worst - wyspa - step - eval",self.island,self.step_num,self.evaluations)
            emigrantsnum = self.dist.worstTab(population, self.number_of_emigrants)
            emigrants = [population[i] for i in emigrantsnum]
        else:
            emigrants = [
                population[random.randrange(len(population))]
                for _ in range(0, number_of_emigrants)
            ]
        return emigrants

    def migrate_individuals(self):
        if self.evaluations - self.last_migration_evolution >= self.migration_interval:
            try:
                individuals_to_migrate = self.get_individuals_to_migrate(
                    self.solutions, self.number_of_emigrants
                )
                self.last_migration_evolution = self.evaluations
            except ValueError as ve:
                print(
                    "-- ValueError -- migrate individuals  --",
                    ve.__str__(),
                    " ",
                    self.island,
                    " ",
                    self.step_num,
                )
                return

            self.migration.migrate_individuals(
                individuals_to_migrate, self.step_num, self.island, time.time(), self.island
            )

    def add_new_individuals(self):
        new_individuals, emigration_at_step_num = self.migration.receive_individuals(
            self.step_num, self.evaluations
        )

        if len(new_individuals) > 0:
            self.nowi = True
            emigration_at_step_num["destinTimestamp"] = time.time()
            emigration_at_step_num["destinMaxFitness"] = self.lastBest
            self.tab_emigr[self.step_num] = emigration_at_step_num
            self.solutions.extend(list(new_individuals))
    
    # MAIN PART - GENETIC ALGORITHM STEP
    def step(self):
        self.step_num = self.step_num + 1

        if 1 == self.step_num:
            self.migration.wait_for_all_start()

            self.lastBest = self.solutions[0].fitness

            # start measuring time
            self.migration.start_time_measure()

        # MIGRACJE
        self.nowi = False
        if self.number_of_islands > 1:
            self.migrate_individuals()
            # todo: SPR CZY MIGRANT POPRAWIŁ WYNIK WYSPY - best w population[0] > best
            try:
                # print("Island %s iter: %s get popu" % (self.island, self.step_num))
                self.add_new_individuals()
            except:
                pass

        self.emas.iteration(self.step_num)
        
        self.emas.alive_count.append(len(self.emas.agents))
        self.emas.energy_data_sum.append(sum([i.energy for i in self.emas.agents]))
        self.emas.energy_data_avg.append(sum([i.energy for i in self.emas.agents])/len(self.emas.agents))
        self.emas.best_fit.append(min(self.emas.agents, key=lambda a: a.fitness).fitness)
        self.emas.variance.append(sum(np.var([i.x for i in self.emas.agents], axis=0)))

        self.solutions.sort(key=lambda agent: agent.fitness)

        # Jeśli W KRZYŻWOANIU I MUTACJI POWSTAŁ LEPSZY
        if not (self.lastBest == self.solutions[0].fitness):
            self.lastBest = self.solutions[0].fitness

        if self.step_num % 5 == 0:
            self.migration.end_time_measure()
            self.lastBest = self.solutions[0].fitness
            self.ctrl.endOfProcess(
                self.island, self.lastBest
            )

            self.migration.signal_finish()

            if self.island == 0:
                self.migration.wait_for_finish()
                self.ctrl.endOfWholeProbe(self.seria)
        
        self.evaluations += 1#len(self.solutions)


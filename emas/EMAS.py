from Config import Config
from Agent import Agent
from random import shuffle
from matplotlib import pyplot as plt
from numpy import var
from time import time
import numpy as np


class EMAS:

    def __init__(self, config: Config):
        self.config = config
        self.agents = config.agents

        self.alive_count = [len(self.agents)]
        self.energy_data_sum = [sum([i.energy for i in self.agents])]
        self.energy_data_avg = [sum([i.energy for i in self.agents])/len(self.agents)]
        self.best_fit = [min(self.agents, key=lambda a: a.fitness).fitness]
        self.variance = [sum(var([i.x for i in self.agents], axis=0))]

    def run(self):
        start_time = time()
        evaluations = 0
        for it in range(self.config.n_iter):
            evaluations += len(self.agents)
            self.iteration(it)
            best_fit = min(self.agents, key=lambda a: a.fitness).fitness
            if it % 10 == 0:
                print("iteration:", it, "agents count:", len(self.agents), "best fit:", best_fit)
            self.alive_count.append(len(self.agents))
            self.energy_data_sum.append(sum([i.energy for i in self.agents]))
            self.energy_data_avg.append(sum([i.energy for i in self.agents])/len(self.agents))
            self.best_fit.append(best_fit)
            self.variance.append(sum(var([i.x for i in self.agents], axis=0)))

        print("runtime: ", time() - start_time, "evals: ", evaluations)

    def iteration(self, it):
        c = self.reproduce()
        self.fight()
        self.remove_dead()
        self.agents.extend(c)
        if it == self.config.n_iter-1:
            best = min([agent for agent in self.agents], key=lambda a: a.fitness)
            print([round(b, 2) for b in best.x])
            print(best.fitness)

    def reproduce(self):
        fitness_average = sum(
            [agent.fitness for agent in self.agents]
        ) / len(self.agents)
        c = []
        p = list(
                filter(
                    lambda a: a.energy > self.config.reproduce_energy,
                    self.agents
                )
            )
        shuffle(p)
        agents_count = len(self.agents)
        for i in range(len(p) // 2):
            offspring = Agent.reproduce(
                p[i],
                p[len(p) // 2 + i],
                self.config.energy_reproduce_loss_coef,
                self.config.cross_coef,
                self.config.mutation_coef,
                self.config.alive_energy,
                fitness_average,
                self.config.n_agent,
                agents_count
            )
            agents_count += len(offspring)
            c.extend(offspring)
        
        return c

    def fight(self):
        shuffle(self.agents)

        n = len(self.agents) // 2
        for i in range(n):
            a1, a2 = self.agents[i], self.agents[n+i]
            if a1.fitness > a2.fitness:
                a1, a2 = a2, a1
            
            energy_loss = a2.energy * self.config.energy_fight_loss_coef

            diff = np.sum(np.abs(np.array(a1.x) - np.array(a2.x)))
            diff /= (a1.upper_bound - a1.lower_bound)
            diff /= len(a1.x)

            energy_loss += a2.energy * (1-diff) * self.config.energy_diff_loss_coef
            if a2.energy - energy_loss < self.config.alive_energy:
                energy_loss = a2.energy - self.config.alive_energy
            
            a1.energy += (energy_loss + self.config.alive_energy)
            a2.energy -= (energy_loss + self.config.alive_energy)

    def remove_dead(self):
        self.agents = [
            agent for agent in self.agents
            if agent.energy > self.config.alive_energy
        ]

    def summary(self):
        iter = [i for i in range(self.config.n_iter + 1)]
        # plt.plot(iter, self.alive_count)
        # plt.plot(iter, self.energy_data_sum)
        # plt.plot(iter, self.energy_data_avg)
        # plt.plot(iter, self.variance)
        plt.plot(iter, self.best_fit)
        plt.show()

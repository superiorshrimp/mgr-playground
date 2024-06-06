from Config import Config
from Agent import Agent
from random import choice, shuffle
from matplotlib import pyplot as plt


class EMAS:

    def __init__(self, config: Config):
        self.config = config
        self.agents = config.agents

        self.alive_count = [len(self.agents)]
        self.energy_data1 = [sum([i.energy for i in self.agents])]
        self.energy_data2 = [sum([i.energy for i in self.agents])/len(self.agents)]
        self.best_fit = [min(self.agents, key=lambda a: a.fitness).fitness]

    def run(self):
        for it in range(self.config.n_iter):
            self.iteration(it)
            best_fit = min(self.agents, key=lambda a: a.fitness).fitness
            print("iteration:", it, "agents count:", len(self.agents), "best fit:", best_fit)
            self.alive_count.append(len(self.agents))
            self.energy_data1.append(sum([i.energy for i in self.agents]))
            self.energy_data2.append(sum([i.energy for i in self.agents])/len(self.agents))
            self.best_fit.append(best_fit)


    def iteration(self, it):
        self.reproduce()
        self.fight()
        self.remove_dead()
        if it == self.config.n_iter-1:
            best = min([agent for agent in self.agents], key=lambda a: a.fitness)
            print([round(b, 2) for b in best.x])
            print(best.fitness)
        

    def reproduce(self):
        shuffle(self.agents)
        fit_avg = sum([agent.fitness for agent in self.agents]) / len(self.agents)
        p, c = [], []
        for i in range(len(self.agents)):
            p1 = self.agents[i]
            if p1.energy > self.config.reproduce_energy and p1 not in p:
                possible_mates = []
                for j in range(len(self.agents)):
                    p2 = self.agents[j]
                    if p2.energy > self.config.reproduce_energy and p1 != p2 and p2 not in p:
                        possible_mates.append(p2)

                if (len(possible_mates) > 0):
                    p2 = choice(possible_mates)
                    c.extend(Agent.reproduce(p1, p2, self.config.energy_reproduce_loss_coef, self.config.cross_coef, self.config.mutation_coef, fit_avg, self.config.n_agent, len(self.agents)))
                    p.append(p1)
                    p.append(p2)
        
        self.agents.extend(c)

    def fight(self):
        shuffle(self.agents)

        n = len(self.agents) // 2
        for i in range(n):
            a1, a2 = self.agents[i], self.agents[n+i]
            if a1.fitness > a2.fitness:
                a1, a2 = a2, a1
            
            energy_loss = a2.energy * self.config.energy_fight_loss_coef
            if a2.energy - energy_loss < self.config.alive_energy:
                energy_loss = a2.energy - self.config.alive_energy
            
            a1.energy += energy_loss
            a2.energy -= energy_loss

    def remove_dead(self):
        self.agents = [agent for agent in self.agents if agent.energy > self.config.alive_energy]

    def summary(self):
        iter = [i for i in range(self.config.n_iter + 1)]
        plt.plot(iter, self.alive_count)
        # plt.plot(iter, self.energy_data1)
        # plt.plot(iter, self.energy_data2)
        plt.plot(iter, self.best_fit)
        plt.show()

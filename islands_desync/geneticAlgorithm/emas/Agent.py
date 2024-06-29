from random import random
from scipy.stats import truncnorm
from .Problem import Problem


class Agent:
    
    def __init__(
        self,
        x: list[float],
        energy: float,
        problem: Problem,
        lower_bound: float,
        upper_bound: float
    ):
        self.x = x
        self.energy = energy
        self.problem = problem
        self.fitness = problem.evaluate(x)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @staticmethod
    def crossover(p1, p2, split: float):
        c1, c2 = [], []

        for i in range(len(p1.x)):
            if random() < split:
                c1.append(p1.x[i])
                c2.append(p2.x[i])
            else:
                c1.append(p2.x[i])
                c2.append(p1.x[i])

        return c1, c2

    def mutate(self, mutation_coef: float):
        for i in range(len(self.x)):
            if random() < mutation_coef:
                self.x[i] = get_truncated_normal(
                    mean = self.x[i],
                    sd=1,
                    low=self.lower_bound,
                    upp=self.upper_bound
                )

        self.fitness = self.problem.evaluate(self.x)

    @staticmethod
    def reproduce(
        p1,
        p2,
        energy_reproduce_loss_coef: float,
        cross_coef: float,
        mutation_coef: float,
        fitness_average: float,
        n_agent: int,
        agents_count: int
    ):
        init_energy1 = p1.energy * energy_reproduce_loss_coef
        init_energy2 = p2.energy * energy_reproduce_loss_coef
        init_energy = init_energy1 + init_energy2
        
        p1.energy -= init_energy1
        p2.energy -= init_energy2

        c1_x, c2_x = Agent.crossover(p1, p2, cross_coef)
        c1 = Agent(
            c1_x, init_energy, p1.problem, p1.lower_bound, p1.upper_bound
        )
        c2 = Agent(
            c2_x, init_energy, p1.problem, p1.lower_bound, p1.upper_bound
        )

        if c1.fitness < fitness_average: c1.mutate(mutation_coef / 2)
        else: c1.mutate(mutation_coef * 2)
        if c2.fitness < fitness_average: c2.mutate(mutation_coef / 2)
        else: c2.mutate(mutation_coef * 2)

        if agents_count < n_agent / 2:
            if c1.fitness < fitness_average and c2.fitness < fitness_average:
                # c1.energy /= 2 + 1
                # c2.energy /= 2
                return [c1, c2]
        return [c1] if c1.fitness < c2.fitness else [c2]

def get_truncated_normal(mean, sd, low, upp):
    return truncnorm.rvs(
        (low - mean) / sd,
        (upp - mean) / sd, 
        loc=mean,
        scale=sd
    )

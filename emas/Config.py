from Problem import Problem
from Agent import Agent
from random import uniform


class Config:

    def __init__(
            self,
            problem: Problem,
            n_agent: int,
            n_iter: int,
            lower_bound: float,
            upper_bound: float,
            start_energy: float,
            reproduce_energy: float,
            alive_energy: float,
            energy_reproduce_loss_coef: float,
            energy_diff_loss_coef: float,
            energy_fight_loss_coef: float,
            cross_coef: float,
            mutation_coef: float,
    ):
        assert n_agent > 0
        assert n_iter > 0
        assert lower_bound < upper_bound
        assert start_energy > 0.0
        assert reproduce_energy > 0.0
        assert alive_energy < start_energy
        assert 0.0 <= energy_reproduce_loss_coef <= 1.0
        assert 0.0 <= energy_fight_loss_coef <= 1.0
        assert 0.0 <= energy_diff_loss_coef <= 1.0
        assert 0.0 <= cross_coef <= 1.0
        assert 0.0 <= mutation_coef <= 1.0

        self.problem = problem
        self.n_dim = problem.n_dim

        self.n_agent = n_agent
        self.agents = [
            Agent(
                [uniform(lower_bound, upper_bound) for j in range(self.n_dim)],
                start_energy,
                problem,
                lower_bound,
                upper_bound
            ) for i in range(n_agent)
        ]

        self.n_iter = n_iter

        self.start_energy = start_energy
        self.reproduce_energy = reproduce_energy
        self.alive_energy = alive_energy
        self.energy_reproduce_loss_coef = energy_reproduce_loss_coef
        self.energy_fight_loss_coef = energy_fight_loss_coef
        self.energy_diff_loss_coef = energy_diff_loss_coef
        self.cross_coef = cross_coef
        self.mutation_coef = mutation_coef

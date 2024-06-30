from Problem import Rastrigin
from EMAS import EMAS
from Config import Config

from matplotlib import pyplot as plt

if __name__ == '__main__':
    fitness_log = []
    alive_log = []
    
    for i in range(10):
        config = Config(
            problem=Rastrigin(100),
            n_agent=16,
            n_iter=1000,
            lower_bound=-5.12,
            upper_bound=5.12,
            start_energy=100,
            reproduce_energy=140,
            alive_energy=1,
            energy_reproduce_loss_coef=0.2,
            energy_fight_loss_coef=0.8,
            energy_diff_loss_coef=0.8,
            cross_coef=0.55,
            mutation_coef=0.02,
        )
        emas = EMAS(config)
        emas.run()

        fitness_log.append(emas.best_fit)
        alive_log.append(emas.alive_count)

    iter = [i for i in range(config.n_iter + 1)]
    for i in range(10):
        plt.plot(iter[::10], fitness_log[i][::10])
    plt.savefig('fit.png')
    plt.clf()
    
    for i in range(10):
        plt.plot(iter[::10], alive_log[i][::10])
    plt.savefig('liv.png')

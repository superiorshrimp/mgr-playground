from random import uniform

from Problem import Rastrigin
from EMAS import EMAS
from Config import Config


if __name__ == '__main__':
    config = Config(
        problem=Rastrigin(100),
        n_agent=16*3,
        n_iter=1000,
        lower_bound=-5.12,
        upper_bound=5.12,
        start_energy=100,
        reproduce_energy=150,
        alive_energy=2,
        energy_reproduce_loss_coef=0.1,
        energy_fight_loss_coef=0.2,
        cross_coef=0.55,
        mutation_coef=0.1,
    )

    emas = EMAS(config)
    emas.run()

    emas.summary()

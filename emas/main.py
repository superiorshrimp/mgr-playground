from Problem import Rastrigin
from EMAS import EMAS
from Config import Config


if __name__ == '__main__':
    config = Config(
        problem=Rastrigin(200),
        n_agent=16*3,
        n_iter=1000,
        lower_bound=-5.12,
        upper_bound=5.12,
        start_energy=100,
        reproduce_energy=140,
        alive_energy=1,
        energy_reproduce_loss_coef=0.2,
        energy_fight_loss_coef=0.5,
        cross_coef=0.55,
        mutation_coef=0.02,
    )

    emas = EMAS(config)
    emas.run()

    emas.summary()

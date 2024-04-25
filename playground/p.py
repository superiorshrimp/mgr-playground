from jmetal.problem.singleobjective.unconstrained import Rastrigin
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm, EvolutionaryAlgorithm
from jmetal.operator import SBXCrossover, PolynomialMutation

problem = Rastrigin()
algorithm = GeneticAlgorithm(
    problem=problem,
    population_size=20,
    offspring_population_size=4,
    mutation=PolynomialMutation(probability=1.0 / problem.number_of_variables(), distribution_index=20),
    crossover=SBXCrossover(probability=1.0, distribution_index=20)
)

algorithm.run()
print(algorithm.get_result())
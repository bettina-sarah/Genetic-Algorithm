
import numpy as np
from numpy.typing import NDArray
import random

from gacvm import MutationStrategy, Domains, GeneMutationStrategy


class GenesMutationStrategy(MutationStrategy):
    """Stratégie de mutation qui mute tous les gènes d'un individu à la fois.
    
    La mutation est effectuée sur chaque gène d'un individu avec la probabilité donnée.
    """
    
    def __init__(self) -> None:
        super().__init__('General: Mutate All Genes')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                offspring[:] = domains.random_values()
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)

        
class GenesMutationStrategyWithoutScaling(MutationStrategy):
    """Stratégie de mutation qui mute tous les gènes d'un individu à la fois.
    
    La mutation est effectuée sur chaque gène d'un individu avec la probabilité donnée.
    """
    
    def __init__(self) -> None:
        super().__init__('Shape Optimizer: All Genes Without Scaling')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                offspring[:-1] = domains.random_values()[:-1]
                    
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)



class ShapeOptimizerLocalAllGenesMutationStrategy(MutationStrategy):

    def __init__(self) -> None:
        super().__init__('Shape Optimizer: Mutate All Genes But Explore Locally')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains): 
            if self._rng.random() <= mutation_rate:
                a = domains.random_values()
                b = a - domains.ranges[:,0] 
                c = b * 0.05 
               
                positive = random.random() >= 0.5
                if positive:
                    offspring[:-2] = offspring[:-2] + c[:-2]
                    offspring[-2] = offspring[-2] + (c[-2]*5)
                    offspring[-1] = offspring[-1] + (c[-1]*5)
                     
                else:
                    offspring[:-2] = offspring[:-2] - c[:-2]
                    offspring[-2] = offspring[-2] - (c[-2]*5)
                    offspring[-1] = offspring[-1] - (c[-1])
                
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains) 
       
       
class ShapeOptimizedMutationStrategy(MutationStrategy):
    
    def __init__(self) -> None:
        super().__init__('Shape Optimizer: Combined Optimized Mutation')
        self.__mutation1 = GeneMutationStrategy() 
        self.__mutation2 = GenesMutationStrategyWithoutScaling() 
        self.__mutation3 = ShapeOptimizerLocalAllGenesMutationStrategy()

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
       rng = np.random.default_rng()
       chiffre = rng.random()
       if chiffre <= 0.02:
           self.__mutation1.mutate(offsprings, mutation_rate, domains)
           
       elif chiffre <= 0.20:
           self.__mutation2.mutate(offsprings, mutation_rate, domains)
       else:
           self.__mutation3.mutate(offsprings, mutation_rate, domains)


class GeneralGenesMutationStrategy(MutationStrategy):
    
    def __init__(self) -> None:
        super().__init__('General : Mutate All Genes But Explore Locally')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains): 
            if self._rng.random() <= mutation_rate:
                a = domains.random_values()
                b = a - domains.ranges[:,0] 
                c = b * 0.01
                
                positive = random.random() >= 0.5
                if positive:
                    offspring[:] = offspring[:] + c
                     
                else:
                    offspring[:] = offspring[:] - c
                
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains) 


class GeneralMultiMutationStrategy(MutationStrategy):
 
    def __init__(self) -> None:
        super().__init__('General: Combined Mutation Strategies')
        self.__mutation1 = GeneMutationStrategy() 
        self.__mutation2 = GenesMutationStrategy()
        self.__mutation3 = GeneralGenesMutationStrategy() 

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
       rng = np.random.default_rng()
       chiffre = rng.random()
       if chiffre <= 0.02:
           self.__mutation1.mutate(offsprings, mutation_rate, domains)
           
       elif chiffre <= 0.20:
           self.__mutation2.mutate(offsprings, mutation_rate, domains)
       else:
           self.__mutation3.mutate(offsprings, mutation_rate, domains)



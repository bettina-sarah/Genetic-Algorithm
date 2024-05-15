
import numpy as np
from numpy.typing import NDArray
import random

from gacvm import MutationStrategy, Domains, GeneMutationStrategy


class GenesMutationStrategy(MutationStrategy):
    """Stratégie de mutation qui mute tous les gènes d'un individu à la fois.
    
    La mutation est effectuée sur chaque gène d'un individu avec la probabilité donnée.
    """
    
    def __init__(self) -> None:
        super().__init__('Mutate All Genes')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                offspring[:] = domains.random_values()
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)

        #domains.ranges_span



        # return self._scale_normalized(self._rng.random(self._ranges.shape[0]))
        
class GenesMutationStrategyWithoutScaling(MutationStrategy):
    """Stratégie de mutation qui mute tous les gènes d'un individu à la fois.
    
    La mutation est effectuée sur chaque gène d'un individu avec la probabilité donnée.
    """
    
    def __init__(self) -> None:
        super().__init__('Mutate All Genes')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                #a = domains.random_values()[-1]
                #b = a - domains.ranges[-1]
                #c = b * 0.05
                #offspring[-1] = offspring[-1] + (c[-1]*5)
                offspring[:-1] = domains.random_values()[:-1]
                
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)



class MixedGenesMutationStrategy(MutationStrategy):
    """Stratégie de mutation qui mute, selon
    """
    
    def __init__(self) -> None:
        super().__init__('Mutate All Genes But Add a Little Spice')

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
        # print(offsprings)
        def do_mutation(offspring, mutation_rate, domains): # un a la fois
            if self._rng.random() <= mutation_rate:
                a = domains.random_values() # 666  # 0.03
                b = a - domains.ranges[:,0] # prend le minimum de ton range # 166 (666 - 500) # 0.2 - 10 = 9.8
                c = b * 0.05 # la nouvelle valeur dans le comrpessed range
                # compressed_values = (a.ranges_span) * 0.01 
                # offspring[:] = domains.random_values()
                # print(offspring)
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
       
       
class SuperMixedGenesMutationStrategy(MutationStrategy):
    """Stratégie de mutation qui mute, selon
    """
    
    
    def __init__(self) -> None:
        super().__init__('Super Duper Mutate All Genes But Add a LOT of Spice')
        self.__mutation1 = GeneMutationStrategy() # 2%
        self.__mutation2 = GenesMutationStrategyWithoutScaling() # 8%
        self.__mutation3 = MixedGenesMutationStrategy() #89%

    def mutate(self, offsprings : NDArray, mutation_rate : float, domains : Domains) -> None:
       rng = np.random.default_rng()
       chiffre = rng.random()
       if chiffre <= 0.02:
           self.__mutation1.mutate(offsprings, mutation_rate, domains)
           
       elif chiffre <= 0.20:
           self.__mutation2.mutate(offsprings, mutation_rate, domains)
       else:
           self.__mutation3.mutate(offsprings, mutation_rate, domains)

# if __name__ == "__main__":
#     strat = MixedGenesMutationStrategy()
    
#     domains = Domains(np.array([[0., 100], [0,1],[-10,10]]), ("dim1","dim2", "dim3"))
#     offspring = np.array((57,0.3,-4), dtype=np.float32)
#     offspring1 = np.array((80,0.7,-5), dtype=np.float32)
   
#     offsprings = np.vstack((offspring, offspring1))
#     strat.mutate(offsprings, 1, domains)


        


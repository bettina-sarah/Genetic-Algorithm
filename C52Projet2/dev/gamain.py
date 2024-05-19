
import sys


from gaapp import QGAApp

from ga_strategy_genes_mutation import GenesMutationStrategy, GenesMutationStrategyWithoutScaling, GeneralGenesMutationStrategy, GeneralMultiMutationStrategy, ShapeOptimizedMutationStrategy, ShapeOptimizerLocalAllGenesMutationStrategy
from gacvm import GeneMutationStrategy
from ga_problem_unknown_number import QUnknownNumberProblemPanel
from ga_problem_open_box import QOpenBoxProblemPanel

from ga_problem_shape_optimizer import QShapeProblemPanel
from ga_problem_yeux_bleu import QEyeProblemPanel


from PySide6.QtWidgets import QApplication

from __feature__ import snake_case, true_property



def main():
    # Création de l'application Qt
    # -----------------------------------------------
    app = QApplication(sys.argv)
    
    # Création de l'application de résolution de problèmes génétiques
    # -----------------------------------------------
    ga_app = QGAApp()
    
    # Exemples d'ajout de stratégies : sélection, croisement et mutation
    # -----------------------------------------------
    # ga_app.add_selection_strategy(...)
    # ga_app.add_crossover_strategy(...)
   
    ga_app.add_mutation_strategy(GenesMutationStrategy)
    ga_app.add_mutation_strategy(GenesMutationStrategyWithoutScaling)    
    ga_app.add_mutation_strategy(ShapeOptimizerLocalAllGenesMutationStrategy)
    ga_app.add_mutation_strategy(ShapeOptimizedMutationStrategy)  
    ga_app.add_mutation_strategy(GeneralGenesMutationStrategy) 
    ga_app.add_mutation_strategy(GeneralMultiMutationStrategy)      

    # Exemple d'ajout de panneau de résolution de problème
    # -----------------------------------------------
    # Problème de la boîte ouverte
    ga_app.add_solution_panel(QUnknownNumberProblemPanel(-1000.0, 0.0, 1000.0))     
    ga_app.add_solution_panel(QOpenBoxProblemPanel())                               
    ga_app.add_solution_panel(QShapeProblemPanel()) 
    ga_app.add_solution_panel(QEyeProblemPanel()) 
    # ...
    # ga_app.add_solution_panel(...)

    # Affichage et exécution de l'application
    # -----------------------------------------------
    ga_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


import numpy as np
from numpy.typing import NDArray

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtwidgets import QImageViewer, create_scroll_int_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QComboBox, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF

from __feature__ import snake_case, true_property

class QShapeProblemPanel(QSolutionToSolvePanel):
    """Panel to solve the open box problem."""

    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.display_panel()
        
        
    
    def display_panel(self):
        
        
        centre_layout = QVBoxLayout(self)
        
        #param
        param_group_box = QGroupBox('Parameters')
        param_layout = QFormLayout(param_group_box)

        self._value_scroll_bar, obstacle_layout = create_scroll_int_value(0,40,100,"")

        shape_selection = QComboBox()
        
        shapes = ['Triangle','Square','Star','Pentagon']
        for i in shapes:
            shape_selection.add_item(i)
        #à modifier avce les values du canvas
        size_label = QLabel('---')
        param_layout.add_row('Canvas size', size_label)
        param_layout.add_row('Obstacle count:', obstacle_layout)
        param_layout.add_row('Shape:', shape_selection)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        #visualization
        visualizaion_layout = QVBoxLayout()

        centre_layout.add_widget(param_group_box )
        centre_layout.add_layout(visualizaion_layout)
        pass
       
        
    @property
    def unknown_value(self) -> float:
        """La valeur recherchée par l'algorithme génétique."""
        return self._value_scroll_bar.get_real_value()

    @property
    def name(self) -> str: # note : override
        """Nom du problème."""
        return 'Problème d’optimisation géométrique'

    @property
    def summary(self) -> str: # note : override
        """Résumé du problème."""
        return '''On cherche à trouver la transformation géométrique permettant de disposer la plus grande forme géométrique sur une surface parsemée d’obstacle.'''

    @property
    def description(self) -> str: # note : override
        """Description du problème."""
        return '''On cherche à trouver la transformation géométrique permettant de disposer la plus grande forme géométrique sur une surface parsemée d’obstacle.'''
    
    def __call__(self, chromosome : NDArray) -> float:
        pass
    
    @property
    def default_parameters(self) -> Parameters:
 
        #a remplacer
        engine_parameters = Parameters()
        engine_parameters.maximum_epoch = 0
        engine_parameters.population_size =0
        engine_parameters.elitism_rate = 0
        engine_parameters.selection_rate = 0
        engine_parameters.mutation_rate = 0
        return engine_parameters
    
        raise NotImplementedError()


    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:
        pass
    
    
    @property
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        
        La définition du problème inclu les domaines des chromosomes et la fonction objective.
        """
        #a remplacer avec le notre
        domains = Domains(np.array([[0., 0]]), ('Size of cutout',))
        return ProblemDefinition(domains, self)   
        
    @Slot()
    def _update_from_configuration(self):
        """Met à jour la visualisation de la boîte en fonction de la configuration."""
        self._update_from_simulation(None)
        
    @Slot()
    def update_solution(self, ga : GeneticAlgorithm) -> None:
        """Slot provoquant la mise à jour de l'interface utilisateur du panneau.
        
        Attention, cette fonction n'est pas destinée à être 'override'."""
        # self._update_from_simulation(ga)

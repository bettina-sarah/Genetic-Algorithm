import numpy as np
from numpy.typing import NDArray

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtwidgets import QImageViewer, create_scroll_real_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF

from __feature__ import snake_case, true_property

class QShapeOptimizerPanel(QSolutionToSolvePanel):
    
    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.__canvas = QRectF(0,0,500,250)
        self.__polygon = QPolygonF()
        
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(1,1))
        self.__polygon.append(QPointF(-1,1))
        
        self.__max_scaling = min(self.__canvas.width(),self.__canvas.height()) / 2
        
        self.__nuage_point = []
    
    
    @property
    def name(self) -> str:
        """Retourne le nom du problème."""
        return 'Shape'

    @property
    def summary(self) -> str:
        """Retourne un résumé du problème."""
        return '''Le problème de la boîte ouverte est un problème d'optimisation bien connu qui consiste à maximiser le volume d'une boiîte pouvant être formée à partir d'une surface rectangulaire.'''

    @property
    def description(self) -> str:
        """Retourne une description détaillée du problème."""
        return '''On cherche à obtenir la plus grande boîte sans couvert à partir d'une surface rectangulaire de taille fixe et connue : largeur et hauteur. L'idée consiste à déterminer la taille des coins carrés à découper pour permettre la formation de la boîte en repliant les 4 côtés restants. '''

        
        
        
        
    def __call__(self, chromosome : NDArray) -> float:
        """Retourne le volume de la boîte obtenue en fonction de la taille de la découpe."""
        
        translation_x = chromosome[0]
        translation_y = chromosome[1]
        rotation = chromosome[2]
        scaling = chromosome[3]
        
        transform = QTransform()
        # transform prend les translations, rotation, scaling
        #transform sur le Polygon
        
        # canvas.contains (polygon.boundingRect) si vrai return point 0
        
        # polygon.containsPoint(nuage_points[:]) si vrai return point 0
        
        # return aire du polygon
        return 1
    
    @property
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        
        La définition du problème inclu les domaines des chromosomes et la fonction objective.
        """
        domains = Domains(np.array([[0,self.__canvas.width()],[0,self.__canvas.height()],[0,359],[0.1,self.__max_scaling]]),('Translate_x','Translate_y','Rotation','Scaling'))
        return ProblemDefinition(domains, self)

    @property
    def default_parameters(self) -> Parameters:
        """Retourne les paramètres par défaut de l'algorithme génétique.
        
        Ces paramètres sont utilisés pour initialiser les paramètres de l'interface graphique 
        et remplace ceux en place.
        """
        engine_parameters = Parameters()
        engine_parameters.maximum_epoch = 100
        engine_parameters.population_size = 20
        engine_parameters.elitism_rate = 0.1
        engine_parameters.selection_rate = 0.75
        engine_parameters.mutation_rate = 0.25
        return engine_parameters

    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:
        # """Met à jour la visualisation de la boîte en fonction de la simulation.
        
        # Note : Cette fonction est un override!.
        # """
        # image = QImage(QSize(self._visualization_widget.width - 1, self._visualization_widget.height - 1), QImage.Format_ARGB32)
        # image.fill(self._background_color)
        # painter = QPainter(image)
        # painter.set_pen(Qt.NoPen)

        # ratio = min(self._visualization_widget.width / self.width, self._visualization_widget.height / self.height) * self._box_visualization_ratio
        # box_visualization_size = QSizeF(self.width * ratio, self.height * ratio)

        # if ga: # evolving, displaying best solution
        #     cutout_size = ga.history.best_solution[0]
        #     cutout_visualization_size = cutout_size * ratio

        #     # self._draw_cut_box_v1(painter, box_visualization_size, cutout_visualization_size)
        #     self._draw_cut_box_v2(painter, box_visualization_size, cutout_visualization_size)

        # else: # not evolving, meaning configuration is in process! displaying uncut box
        #     self._draw_uncut_box(painter, box_visualization_size)


        # painter.end()
        # self._visualization_widget.image = image
        pass
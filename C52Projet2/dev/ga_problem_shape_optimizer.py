import numpy as np
from numpy.typing import NDArray

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtgui import process_area
from uqtwidgets import QImageViewer, create_scroll_int_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QComboBox, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF

from __feature__ import snake_case, true_property

class QShapeProblemPanel(QSolutionToSolvePanel):
    
    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.display_panel()
        
        self.__canvas = QRectF(0,0,500,250)
        self.__polygon = QPolygonF()
        
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(1,1))
        self.__polygon.append(QPointF(-1,1))
        
        self.__max_scaling = min(self.__canvas.width(),self.__canvas.height()) / 2
        self.__rng = np.random.default_rng()
        self.__point_quantity = 20
        self.__nuage_point = []
        # a connecter au scroller du GUI
        self.populate_nuage()


        # # peut-etre remettre un array normal pour le nuage de points
        # self.__nuage_point = np.empty((20, 2))
        # # pour les tests...
        # self.__nuage_point[:,0] = self.__rng.uniform(0,self.__canvas.width())
        # self.__nuage_point[:,1] = self.__rng.uniform(0,self.__canvas.height())
    
    
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
    
  
    
    @property
    def default_parameters(self) -> Parameters:
 
        #a remplacer
        engine_parameters = Parameters()
        engine_parameters.maximum_epoch = 100
        engine_parameters.population_size = 20
        engine_parameters.elitism_rate = 0.1
        engine_parameters.selection_rate = 0.75
        engine_parameters.mutation_rate = 0.25
        return engine_parameters
    
        raise NotImplementedError()
        
        
    def __call__(self, chromosome : NDArray) -> float:
        """Retourne le volume de la boîte obtenue en fonction de la taille de la découpe."""
        
        translation_x = chromosome[0]
        translation_y = chromosome[1]
        rotation = chromosome[2]
        scaling = chromosome[3]
        
        transform = QTransform()
        # transform prend les translations, rotation, scaling
        #transform sur le Polygon
        transform.translate(translation_x, translation_y)
        transform.rotate(rotation)
        transform.scale(scaling, scaling)
        polygon_transformed = transform.map(self.__polygon)

        # canvas.contains (polygon.boundingRect) si vrai return point 0
        if not self.__canvas.contains(polygon_transformed.bounding_rect()):
            return 0.1
        
        
        # polygon.containsPoint(nuage_points[:]) si vrai return point 0
        #range
        for i in range(self.__point_quantity):
            if polygon_transformed.contains_point(self.__nuage_point[i],Qt.OddEvenFill):
                return 0.1
        
        # return aire du polygon
        return process_area(polygon_transformed)
    
    def populate_nuage(self):
        for _ in range(self.__point_quantity):
            self.__nuage_point.append(QPointF(self.__rng.uniform(0,self.__canvas.width()),self.__rng.uniform(0,self.__canvas.height())))
    
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
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        La définition du problème inclu les domaines des chromosomes et la fonction objective."""
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


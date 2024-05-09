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
        
        
        self.__canvas = QRectF(0,0,500,250)
        self.__polygon = QPolygonF()
        #pour les tests on cree un carre
        self.create_hexagon()
        self.__max_scaling = min(self.__canvas.width(),self.__canvas.height()) / 2

        self.display_panel()
        self.__obstacle_size = 4

        self.__rng = np.random.default_rng()
        self.__point_quantity = 40

        self.__nuage_point = []
        # a connecter au scroller du GUI
        self.populate_nuage()
        self.__transformed_shapes = []


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
        area = 0
        # canvas.contains (polygon.boundingRect) si vrai return point 0
        if not self.__canvas.contains(polygon_transformed.bounding_rect()):
            return area
        
        
        # polygon.containsPoint(nuage_points[:]) si vrai return point 0
        #range
        for i in range(self.__point_quantity):
            if polygon_transformed.contains_point(self.__nuage_point[i],Qt.OddEvenFill):
                return area
        area = process_area(polygon_transformed)
        
        self.__transformed_shapes.append((polygon_transformed,area))
        # return aire du polygon
        return area
    
    def create_square(self):
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(1,1))
        self.__polygon.append(QPointF(-1,1))

    def create_triangle(self):
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(0,1))

    def create_hexagon(self):
        self.__polygon.append(QPointF(-1,-0.5))
        self.__polygon.append(QPointF(-1,0.5))
        self.__polygon.append(QPointF(-0.5,1))
        self.__polygon.append(QPointF(0.5,1))
        self.__polygon.append(QPointF(1,0.5))
        self.__polygon.append(QPointF(1,-0.5))
        self.__polygon.append(QPointF(0.5,-1))
        self.__polygon.append(QPointF(-0.5,-1))

    def create_star(self):
        self.__polygon.append(QPointF(-1,0))
        self.__polygon.append(QPointF(-0.25,0.25))
        self.__polygon.append(QPointF(0,1))
        self.__polygon.append(QPointF(0.25,0.25))
        self.__polygon.append(QPointF(1,0))
        self.__polygon.append(QPointF(0.25,-0.25))
        self.__polygon.append(QPointF(0,-1))
        self.__polygon.append(QPointF(-0.25,-0.25))
        
    
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
        visualization_group_box = QGroupBox('Visualization')
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        visualization_layout = QGridLayout(visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        visualization_layout.add_widget(self._visualization_widget)
        
        centre_layout.add_widget(param_group_box )
        centre_layout.add_widget(visualization_group_box)
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

    def _draw_obstacles(self, painter):
        painter.save()
        painter.set_brush(QColor(138, 223, 43))
        for p in self.__nuage_point:
            painter.draw_rect(p.x(),
                              p.y(),
                              self.__obstacle_size,
                              self.__obstacle_size)
            
        painter.restore() 
        pass
    
    def _draw_shapes(self, painter):
        painter.save()
        painter.set_brush(QColor(255, 0, 255))
        #sort le tableau
        self.__transformed_shapes.sort(key=lambda x: x[1])
        painter.draw_polygon(self.__transformed_shapes[0][0]) 
        
        painter.set_brush(Qt.NoBrush)
        painter.set_pen(QColor(255, 0, 255))
        for shape in self.__transformed_shapes:
            painter.draw_polygon(shape[0]) 
            
        self.__transformed_shapes.clear()
        painter.restore()
        #flush le tableau
        pass

    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:

        #Qpainter
        #crée un image de la grosseur du visualization+box
        image = QImage(QSize(500, 250), QImage.Format_ARGB32)
        # image.fill( QColor(255, 255, 255))
        #image devient parent du painter
        painter = QPainter(image)
        painter.set_pen(Qt.NoPen)
        painter.set_brush(QColor(39, 45, 46))
        painter.draw_rect(self.__canvas) 
        
               
        
        self._visualization_widget.image = image
        self._box_visualization_ratio = 0.9  
        self._draw_obstacles(painter)
        if len(self.__transformed_shapes)>0:
            self._draw_shapes(painter)
        
        painter.end()
        pass


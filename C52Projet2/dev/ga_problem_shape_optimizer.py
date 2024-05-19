import numpy as np
from numpy.typing import NDArray

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtgui import process_area
from uqtwidgets import QImageViewer, create_scroll_int_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QComboBox, QFormLayout, QGroupBox, QGridLayout, QSizePolicy, QPushButton
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF, Signal

from __feature__ import snake_case, true_property

class QShapeProblemPanel(QSolutionToSolvePanel):
    
    obstacle_count_changed = Signal(int)
    
    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
        
        
        self.__canvas = QRectF(0,0,500,250)
        self.__polygon = QPolygonF()
        #pour les tests on cree un carre
        # self.create_triangle()
        self.__translation_x 
        self.__translation_y
        self.__rotation 
        self.__scaling
        self.__max_scaling = min(self.__canvas.width(),self.__canvas.height()) / 2

        self.__display_panel()
        self.__obstacle_size = 4

        self.__rng = np.random.default_rng()
        self.__point_quantity = 70

        self.__nuage_point = []
        # a connecter au scroller du GUI
        self.__populate_nuage()

        
        self.__areas = np.empty(0, dtype=float)
        
        self.__shape_map = {
        "Triangle":self.create_triangle,
        "Square":self.create_square,
        "Star":self.create_star,
        "Hexagon":self.create_hexagon
        }
        
        self.__shape_map[self.__shape_selection.current_text]()
        self.__shapes = np.empty((0,self.__shape_points_count), dtype=QPolygonF)


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
    
  
    def __call__(self, chromosome : NDArray) -> float:
        """Retourne le volume de la boîte obtenue en fonction de la taille de la découpe."""
        
        self.__translation_x = chromosome[0]
        self.__translation_y = chromosome[1]
        self.__rotation = chromosome[2]
        self.__scaling = chromosome[3]
        
        transform = QTransform()
        # transform prend les translations, rotation, scaling
        #transform sur le Polygon
        transform.translate(self.__translation_x, self.__translation_y)
        transform.rotate(self.__rotation)
        transform.scale(self.__scaling, self.__scaling)
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

        self.__shapes = np.vstack([self.__shapes,[polygon_transformed]])
        self.__areas = np.append(self.__areas, area)

        return area
    
    def create_square(self):
        self.__polygon.clear()
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(1,1))
        self.__polygon.append(QPointF(-1,1))
        self.__shape_points_count = 4

    def create_triangle(self):
        self.__polygon.clear()
        self.__polygon.append(QPointF(-1,-1))
        self.__polygon.append(QPointF(1,-1))
        self.__polygon.append(QPointF(0,1))
        self.__shape_points_count = 3

    def create_hexagon(self):
        self.__polygon.clear()
        self.__polygon.append(QPointF(-1,-0.5))
        self.__polygon.append(QPointF(-1,0.5))
        self.__polygon.append(QPointF(-0.5,1))
        self.__polygon.append(QPointF(0.5,1))
        self.__polygon.append(QPointF(1,0.5))
        self.__polygon.append(QPointF(1,-0.5))
        self.__polygon.append(QPointF(0.5,-1))
        self.__polygon.append(QPointF(-0.5,-1))
        self.__shape_points_count = 8

    def create_star(self):
        self.__polygon.clear()
        self.__polygon.append(QPointF(-1,0))
        self.__polygon.append(QPointF(-0.25,0.25))
        self.__polygon.append(QPointF(0,1))
        self.__polygon.append(QPointF(0.25,0.25))
        self.__polygon.append(QPointF(1,0))
        self.__polygon.append(QPointF(0.25,-0.25))
        self.__polygon.append(QPointF(0,-1))
        self.__polygon.append(QPointF(-0.25,-0.25))
        self.__shape_points_count = 8
        

    
    def populate_nuage(self):
        for _ in range(self.__point_quantity):
            self.__nuage_point.append(QPointF(self.__rng.uniform(0,self.__canvas.width()),self.__rng.uniform(0,self.__canvas.height())))
    
    def display_panel(self):
        
        
        self.__centre_layout = QVBoxLayout(self)
        
        #param
        self.__param_group_box = QGroupBox('Parameters')
        self.__param_layout = QFormLayout(self.__param_group_box)

        self.__value_scroll_bar, self.__obstacle_layout = create_scroll_int_value(0,40,100,"")
        self.__regenerate_button = QPushButton('Regenerate')
        self.__regenerate_button.set_fixed_width(80)
        self.__obstacle_layout.add_widget(self.__regenerate_button)
        
        self.__value_scroll_bar.valueChanged.connect(self.update_point_quantity)
        self.__regenerate_button.pressed.connect(self.update_nuage)

        # privé 
        self.__shape_selection = QComboBox()
        
        shapes = ['Triangle','Square','Star','Hexagon']
        for i in shapes:
            self.__shape_selection.add_item(i)
            
        self.__shape_selection.currentTextChanged.connect(self.choose_shape)
        #à modifier avce les values du canvas
        self.__size_label = QLabel(str(int(self.__canvas.width())) + ' x ' + str(int(self.__canvas.height()))) 
        self.__param_layout.add_row('Canvas size', self.__size_label)
        self.__param_layout.add_row('Obstacle count:', self.__obstacle_layout)
        self.__param_layout.add_row('Shape:', self.__shape_selection)
        self.__param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        #visualization
        self.__visualization_group_box = QGroupBox('Visualization')
        self.__visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.__visualization_layout = QGridLayout(self.__visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        self.__visualization_layout.add_widget(self.__visualization_widget)
        
        self.__centre_layout.add_widget(self.__param_group_box )
        self.__centre_layout.add_widget(self.__visualization_group_box)
        pass
    
    @Slot()
    def update_point_quantity(self):
        self.__point_quantity = self.__value_scroll_bar.value
        self.__nuage_point.clear()
        self.populate_nuage()
        
        self._draw_obstacles(self.painter_prepare_obstacles())
        
        
    @Slot()
    def update_nuage(self):
        self.__nuage_point.clear()
        self.populate_nuage()
        self._draw_obstacles(self.painter_prepare_obstacles())
        
    @Slot()
    def choose_shape(self):
        shape = str(self.shape_selection.current_text)
        self.shape_map[shape]()
        self.__shapes = np.empty((0,self.__shape_points_count), dtype=QPolygonF)
        
        print("choose shape !")
        
    def painter_prepare_obstacles(self):
        image = QImage(QSize(500, 250), QImage.Format_ARGB32)
        
        painter = QPainter(image)
        painter.set_pen(Qt.NoPen)
        painter.set_brush(QColor(39, 45, 46))
        painter.draw_rect(self.__canvas) 
        
        self._visualization_widget.image = image
        self._box_visualization_ratio = 0.9
        return painter
        
    
        
        
        
    
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
        painter.set_brush(QColor(100, 0, 255))
        #sort du plus grand au plus petit
        indexes = np.argsort(self.__areas, axis=0)[::-1]
        sorted_shapes = self.__shapes[indexes]

        painter.draw_polygon(QPolygonF(sorted_shapes[0])) 
        painter.set_brush(Qt.NoBrush)
        painter.set_pen(QColor(10, 255, 100))
       
        #numpy me ?
        for i in range(sorted_shapes.shape[0]):
            painter.draw_polygon(QPolygonF(sorted_shapes[i]))
   
        self.__shapes = np.empty((0,self.__shape_points_count), dtype=QPolygonF)
        self.__areas = np.empty(0, dtype=float)
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
        if np.size(self.__areas)>0:
            self._draw_shapes(painter)
        
        painter.end()
        pass


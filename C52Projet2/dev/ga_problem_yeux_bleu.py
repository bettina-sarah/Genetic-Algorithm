import numpy as np
from numpy.typing import NDArray
import math
import random

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtgui import process_area
from uqtwidgets import QImageViewer, create_scroll_int_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QComboBox, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont, QTransform
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis

from __feature__ import snake_case, true_property

class QEyeProblemPanel(QSolutionToSolvePanel):
    
    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
    
        self.__chart_view = QChartView()
        self.display_panel()
        
        self.__canvas = QRectF(0,0,1500,500)
        
        self.__population = 1000
        self.__taux_croissance = 10
        self.__preference = 1
        self.__annee = 1
        
        self.__pop_bleu = 30
        self.__pop_brun = 30
        self.__pop_combo = 30
        
        self.__colors = (QColor(0,0,255),
                         QColor(245,213,162),
                         QColor(165,42,42))
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        
        self.__probabilites_procreation = np.array([[0, 0, 1, 0.25, 0.5],
                                                    [0, 0.5, 0, 0.5, 0.5],
                                                    [1, 0.5, 0, 0.25, 0]],dtype=np.float32)
        print(" ")

    
    @property
    def unknown_value(self) -> float:
        """La valeur recherchée par l'algorithme génétique."""
        return self._value_scroll_bar.get_real_value()

    @property
    def name(self) -> str: # note : override
        """Nom du problème."""
        return 'Problème d’optimisation de pureté de couple de population'

    @property
    def summary(self) -> str: # note : override
        """Résumé du problème."""
        return '''On cherche à trouver la balance parfaite  permettant de disposer la plus grande forme géométrique sur une surface parsemée d’obstacle.'''

    @property
    def description(self) -> str: # note : override
        """Description du problème."""
        return '''On cherche à trouver la transformation géométrique permettant de disposer la plus grande forme géométrique sur une surface parsemée d’obstacle.'''
  
    def __call__(self, chromosome : NDArray) -> float:
        """Retourne le volume de la boîte obtenue en fonction de la taille de la découpe."""
        
        brun = chromosome[0]
        bleu = chromosome[1]
        
        pop_brun = math.floor(self.__population * brun)
        pop_bleu = math.ceil(self.__population * bleu)
        
        pop_combo = self.__population - (pop_brun + pop_bleu)
        
        pop_yeux = np.array([pop_brun,pop_combo,pop_bleu])
        pop_gen = self.__population
        for _ in range(self.__annee):
            couples = np.zeros((5),dtype=int)
            #trouve tous les couples
            couples[0],couples[1] = self.match_bleu(pop_yeux)
            couples[4] = self.match_brun(pop_yeux)
            couples[2] = self.match_couple_final(pop_yeux, 0)
            couples[3] = self.match_couple_final(pop_yeux, 1)
            # ajoute les couples avec le taux de croissance
            couples = couples + self.croissance_couples()
            # trouve la nouvelle distribution de population
            pop_final = (couples  * self.__probabilites_procreation)*2
            pop_final = np.array(np.sum(pop_final, axis=1), dtype=np.uint16)
            # update le nombre total de population
            pop_gen = np.sum(couples)*2
            # ajouter le surplus au combo_brun (un surplus arrive lorsque *__probabilites_procreation donne un .5, mais l'array est en int)
            reste = pop_gen - np.sum(pop_final)
            pop_final[1] += reste
            pop_yeux = pop_final
            
           
        pourcentage_finale = pop_yeux[2]/pop_gen   
        score = 1 - abs(pourcentage_finale-0.50)
        print("score: ",score, " avec ", pourcentage_finale*100, "domaine bleu:",bleu, "brun:",brun)
        
        self.__results = np.vstack((self.__results, pop_yeux))
        self.__scores = np.append(self.__scores, score)
        return score
    
    
    def match_bleu(self,pop_yeux):
        # pop_bleu = pop_yeux[2]
        # pop_combo = pop_yeux[1]
        
        #trouve le restant bleu
        restant_bleu = pop_yeux[2] % 2
        #retire de la population des combos le restant des bleus (0 ou 1)
        
        #accouple tout les bleus ensemble, garde un pourcentage (préférence)
        # couple_bleu_bleu = math.floor(((pop_yeux[2] - restant_bleu) / 2) * self.__preference)
        couple_bleu_bleu = (pop_yeux[2] - restant_bleu)/2
        
        
        if couple_bleu_bleu % 2:
            couple_bleu_bleu *= self.__preference
            couple_bleu_bleu = math.floor(couple_bleu_bleu)
            # pop_yeux[2]+=2
        else:
            couple_bleu_bleu *= self.__preference
            
        # couple_bleu_bleu = math.floor(couple_bleu_bleu)
        #retire de la population bleus le nombre qui s'est acoouplé
        pop_yeux[2] -= couple_bleu_bleu * 2
        #le couple combo_bleu = restant (0,1)
        couple_combo_bleu = pop_yeux[2]
        pop_yeux[2] -= couple_combo_bleu
        pop_yeux[1] -= couple_combo_bleu
        
        return couple_bleu_bleu , couple_combo_bleu
    
    def match_brun(self,pop_yeux):
        # brun =  pop_yeux[0]
        # combo = pop_yeux[1]
        couples_brun_combo = min(pop_yeux[0],  pop_yeux[1])
        pop_yeux[0] -= couples_brun_combo
        pop_yeux[1] -= couples_brun_combo
        
        return couples_brun_combo
    
    # utiliser pour match final sur pop_brun et pop_combo
    def match_couple_final(self, pop_yeux, yeux):
        couples = pop_yeux[yeux] / 2
        pop_yeux[yeux] -= couples * 2
        return couples
    
    
    def croissance_couples(self):
        croissances = np.zeros((5),dtype=int)
        croissances[0] = random.randrange(int(self.__taux_croissance/3),
                                          int(self.__taux_croissance/2))
        
        croissances[1] = random.randrange(int((self.__taux_croissance - croissances[0])/3),
                                            int((self.__taux_croissance - croissances[0])/2))
        
        croissances[2]  = random.randrange(int((self.__taux_croissance - np.sum(croissances[:1]))/3),
                                           int((self.__taux_croissance - np.sum(croissances[:1]))/2))
        
        croissances[3]  = random.randrange(int((self.__taux_croissance - np.sum(croissances[:2]))/3),
                                           int((self.__taux_croissance - np.sum(croissances[:2]))/2))
        
        croissances[4]  = self.__taux_croissance - np.sum(croissances[:-1])
        return croissances
        pass
    
    def display_panel(self):
        
        centre_layout = QVBoxLayout(self)
        
        #param
        param_group_box = QGroupBox('Parameters')
        param_layout = QFormLayout(param_group_box)

        self._value_pop_bleu_sb, pop_bleu_layout = create_scroll_int_value(0,34,100,"")
        self._value_pop_brun_sb, pop_brun_layout = create_scroll_int_value(0,33,100,"")
        self._value_pop_combo_sb, pop_combo_layout = create_scroll_int_value(0,33,100,"")
        
        self._value_pop_bleu_sb.valueChanged.connect(self.update_purete_bleu)
        self._value_pop_brun_sb.valueChanged.connect(self.update_purete_brun)
        self._value_pop_combo_sb.valueChanged.connect(self.update_purete_combo)

        #à modifier avce les values du canvas
        param_layout.add_row('Population bleu:', pop_bleu_layout)
        param_layout.add_row('Population brun:', pop_brun_layout)
        param_layout.add_row('Population combo:', pop_combo_layout)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        #visualization
        visualization_group_box = QGroupBox('Visualization')
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._visualization_layout = QGridLayout(visualization_group_box)
        
        self._visualization_widget = QImageViewer(True)
        self._visualization_layout.add_widget(self._visualization_widget)
        
        centre_layout.add_widget(param_group_box)
        centre_layout.add_widget(visualization_group_box)
        pass
    
    @Slot()
    def update_purete_bleu(self):
        self.__pop_bleu = self._value_pop_bleu_sb.value
        total = self._value_pop_bleu_sb.value + self._value_pop_brun_sb.value + self._value_pop_combo_sb.value
        if total != 100:
            diff = total - 100
            self._value_pop_brun_sb.value= (self._value_pop_brun_sb.value - diff / 2)
            self.__pop_brun = (self._value_pop_brun_sb.value - diff / 2)
            self._value_pop_combo_sb.value = (self._value_pop_combo_sb.value - diff / 2)
            self.__pop_combo = (self._value_pop_combo_sb.value - diff / 2)
        
    @Slot()
    def update_purete_brun(self):
        self.__pop_brun = self._value_pop_brun_sb.value
        total = self._value_pop_bleu_sb.value + self._value_pop_brun_sb.value + self._value_pop_combo_sb.value
        if total != 100:
            diff = total - 100
            self._value_pop_combo_sb.value = (self._value_pop_combo_sb.value - diff / 2)
            self.__pop_combo = (self._value_pop_combo_sb.value - diff / 2)
            self._value_pop_bleu_sb.value= (self._value_pop_bleu_sb.value - diff / 2)
            self.__pop_bleu = (self._value_pop_bleu_sb.value - diff / 2)
    @Slot()
    def update_purete_combo(self):
        self.__pop_combo = self._value_pop_combo_sb.value
        total = self._value_pop_bleu_sb.value + self._value_pop_brun_sb.value + self._value_pop_combo_sb.value
        if total != 100:
            diff = total - 100
            self._value_pop_brun_sb.value= (self._value_pop_brun_sb.value - diff / 2)
            self.__pop_brun = (self._value_pop_brun_sb.value - diff / 2)
            self._value_pop_bleu_sb.value= (self._value_pop_bleu_sb.value - diff / 2)
            self.__pop_bleu = (self._value_pop_bleu_sb.value - diff / 2)
    
    @property
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        La définition du problème inclu les domaines des chromosomes et la fonction objective."""
        domains = Domains(np.array([[0.01,0.49],[0.01,0.49]]),('Brun','Bleu',))
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

    def _draw_chart(self,painter,solution,position):
        x,y,width,height = position
        painter.save()
        painter.set_brush(QColor(0,0,0))
        outer_rect = QRectF(x,y,width,height)
        painter.draw_rect(outer_rect)
        
        inner_width = outer_rect.width() / 3
        inner_height = outer_rect.height()
        
        for i in range(3):
            painter.set_brush(self.__colors[i])
            inner_rect = QRectF(outer_rect.left() + i * inner_width, outer_rect.top(), inner_width, inner_height * (solution[i]/100))
            painter.draw_rect(inner_rect)
        
        painter.restore()
        pass
        
        
        
        
    def _draw_charts_grid(self,painter,size):
        painter.save()
        indexes = np.argsort(self.__scores, axis=0)[::-1]
        sorted_results = self.__results[indexes]
        
        
        
        if np.size(sorted_results) % 2 == 1:
            cells_quantity = np.ma.size(sorted_results,0) + 1
            cells_pair = False
        else:
            cells_quantity = np.ma.size(sorted_results,0)
            cells_pair = True

       # Calculate the number of squares along one dimension
        cols = math.ceil(math.sqrt(cells_quantity))
        rows = math.ceil(cells_quantity / cols)

        # Calculate the size of each square
        squareWidth = size.width() / cols
        squareHeight = size.height() / rows

        # Set the pen for the border (optional)
        pen = QPen(Qt.black)  # Border color
        pen.set_width(1)      # Border width
        painter.set_pen(pen)

        # Draw the squares
        for i in range(cells_quantity):
            # if i == cells_quantity and not cells_pair:
            #    break
            if i == cells_quantity - 1 and not cells_pair:
                 break
            # elif i == cells_quantity:
            #     break
            
            row = i // cols
            col = i % cols
            self._draw_chart(painter,sorted_results[i],(0 + col * squareWidth,
                                                        0 + row * squareHeight,
                                                        squareWidth,
                                                        squareHeight))
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        
        painter.restore()
        pass

    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:
        size =  QSize(1500,500)
        image = QImage(size, QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.set_pen(Qt.NoPen)
        painter.set_brush(QColor(255, 255, 255))
        painter.draw_rect(self.__canvas)
        
        
        self._visualization_widget.image = image
        self._box_visualization_ratio = 0.9
        
        if np.size(self.__results)>0:
            self._draw_charts_grid(painter,size)
            
        painter.end()
        pass


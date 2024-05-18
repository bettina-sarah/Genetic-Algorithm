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

        self.__annee = 20

        # self.__population_brun = 0.85
        # self.__population_combo = 0.07
        # self.__population_bleu = 0.08

        
        self.__probabilites_procreation = np.array([[4, 1, 0, 0, 0, 2],
                                                    [0, 2, 0, 2, 4, 2],
                                                    [0, 1, 4, 2, 0, 0 ]],dtype=np.float32)
                
        # self.__probabilites_procreation = np.array([[1, 0.25, 0, 0, 0, 0.5],
        #                                             [0, 0.5, 0, 0.5, 1, 0.5],
        #                                             [0, 0.25, 1, 0.5, 0, 0 ]],dtype=np.float32)
        #premiere rangée = la valeur decimal de l'array reste converti en nombre binaire
        #deuxieme rangée = l'index du couple combo dans l'array couples_finales
        self.__lookup_table_reste = np.array([[5, 3, 6,],
                                              [4, 3, 5]],dtype=np.uint8)
        # ajouté: brun + bleu = 100% combo; 0% brun et 0% bleu
        self.__population_brun  = self._value_pop_brun_sb.value
        self.__population_combo  = self._value_pop_combo_sb.value
        self.__population_bleu   = self._value_pop_bleu_sb.value
        
        self.__colors = (QColor(0,0,255),
                         QColor(245,213,162),
                         QColor(165,42,42))
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        
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
        
        # purete_brun = chromosome[0]
        # purete_combo = chromosome[1]
        # purete_bleu = chromosome[2]
        
        # chromosome = np.array([0.3,0.5,0.8])
        #conversion % choisis par le user en nbr int de personnes en fonc de population
        
        #refactor pour setter getter ****************************************************************************************
        pop_brun =  self.__population_brun
        pop_combo = self.__population_combo
        pop_bleu =  self.__population_bleu
        
        pop_gen = pop_brun + pop_combo + pop_bleu
        
        r = pop_gen % 2
        pop_gen += r
        pop_combo += r
        
        pop_yeux = np.array([pop_brun, pop_combo, pop_bleu], dtype=np.uint8)
        for _ in range(self.__annee):
            # pop_yeux = np.array([pop_brun, pop_combo, pop_bleu], dtype=np.uint8)
            couples_finales = np.zeros(6, dtype=np.uint8)
            
            #retirer les impaires
            reste = pop_yeux % 2
            pop_yeux = pop_yeux - reste
            # faire couples  et apres, couples pures avec % purete; dtype assure le math.floor
            couples = pop_yeux / 2
            couples_pures = np.array(couples * chromosome, dtype=np.uint8)
            couples_finales[:3] = couples_pures
            
            
            
            # revenir a pop_yeux: faire nos couples diverse (non-pure)
            couples = couples - couples_pures
            pop_yeux = couples * 2 # brun, combo, bleu restants
            # couples_finales[:3]*2
            
            # combos a faire: ORDRE IMPORTANT: bleu-combo , brun-bleu, brun-combo, 
            # couples impures:
            couples_combo = np.zeros(3, dtype=np.uint8)
            
            
            sorted_pop_yeux = np.argsort(pop_yeux)
            
            premier = sorted_pop_yeux[0]
            deuxieme = sorted_pop_yeux[1]
            troisieme = sorted_pop_yeux[2]
            # individus_premier = pop_yeux[premier]/2
            # mask: avoir true quand c'est les gens a coupler
            mask = pop_yeux != pop_yeux[premier]
            #faire soustraction juste sur les elements qui sont true (donc pas les gens les moins nombreux)
            pop_yeux[mask] = pop_yeux[mask] - pop_yeux[premier]/2
            couples_combo[mask] = pop_yeux[premier]/2
            
            #  mtn vider le moins nombreux
            pop_yeux[premier] = 0
        
            couples_combo[premier] = pop_yeux[deuxieme]
            
            pop_yeux[mask] = pop_yeux[mask] - pop_yeux[deuxieme]
            pop_yeux[deuxieme] = 0
            couples_finales[troisieme] = couples_finales[troisieme] + pop_yeux[troisieme] / 2
            
            couples_finales[3:] = couples_combo
            

            if np.sum(reste) > 0:
                # convertie l'array reste(un array binaire) en sa valeur decimal
                decimal_number = np.packbits(np.flip(reste), bitorder='little')
            
                # np where retourne tuple avec array: [index ou la comparaison est vraie, type de variable]
                index_lookup = np.where(self.__lookup_table_reste[0] == decimal_number[0])[0][0]
                
                index_combo = self.__lookup_table_reste[1, index_lookup]
                couples_finales[index_combo] = couples_finales[index_combo] + 1 
            # ---------------------------------------------
            # taux de croissance?
            # couples_finales + self.croissance_hard()
            pop_final = (couples_finales  * self.__probabilites_procreation)*2
            pop_final = np.array(np.sum(pop_final, axis=1), dtype=np.uint16)
            # update le nombre total de population
            #ajouter le surplus au combo_brun (un surplus arrive lorsque *__probabilites_procreation donne un .5, mais l'array est en int)
            accouple = np.sum(pop_final)
            reste = pop_gen - accouple
            pop_final[1] += reste # ajouter reste au combo
            pop_yeux = pop_final
            pop_gen = np.sum(pop_final)
            
            # test
            
           

        # pourcentage_finale = pop_yeux[2]/pop_gen   
        # score = 1 - abs(pourcentage_finale-0.50)
        pourcentage_bleu = pop_yeux[2]/pop_gen  
        pourcentage_brun = pop_yeux[0]/pop_gen
        pourcentage_combo = pop_yeux[1]/pop_gen
        
        # NOTES: slider pour user pour changer le score (33%-33%-33% ou 50%-50% ou etc ... )
        # taux de croissance manque
        score = ((pourcentage_bleu-0.33)**2 + (pourcentage_brun - 0.33)**2 + (pourcentage_combo-0.33)**2)**0.5
        score = 1 - score


        
        self.__results = np.vstack((self.__results, chromosome))
        self.__scores = np.append(self.__scores, score)
        print("---")
        print("brun: ","%7.0f" % self.__population_brun,"| combo","%7.0f" % self.__population_combo,"| bleu","%7.0f" % self.__population_bleu, "| pop_gen:","%7.0f" %pop_gen)
        print("brun: ","%7.4f" % chromosome[0],"| combo","%7.4f" % chromosome[1],"| bleu","%7.4f" % chromosome[2], "|")
        print("brun: ","%7.0f" % pop_yeux[0],"| combo","%7.0f" %pop_yeux[1],"| bleu", "%7.0f" %pop_yeux[2], "|")
        print("brun: ","%7.3f" % pourcentage_brun,"| combo","%7.3f" % pourcentage_combo,"| bleu","%7.3f" % pourcentage_bleu, "| score:","%7.7f" %score)
        return score
  
    
    def croissance_couples(self):
        rng = np.random.default_rng()
        croissance = rng.integers(1, 6, size=6)
        return croissance
    
    def croissance_hard(self):
        array = np.array([3,2,2,1,1,1])
        np.random.shuffle(array)
        return array
        
    
    def display_panel(self):
        
        centre_layout = QVBoxLayout(self)
        
        #param
        param_group_box = QGroupBox('Parameters')
        param_layout = QFormLayout(param_group_box)

        self._value_pop_bleu_sb, pop_bleu_layout = create_scroll_int_value(100,500,1000,"")
        self._value_pop_brun_sb, pop_brun_layout = create_scroll_int_value(100,500,1000,"")
        self._value_pop_combo_sb, pop_combo_layout = create_scroll_int_value(100,500,1000,"")
        
        self._value_pop_bleu_sb.valueChanged.connect(self.update_purete_bleu)
        self._value_pop_brun_sb.valueChanged.connect(self.update_purete_brun)
        self._value_pop_combo_sb.valueChanged.connect(self.update_purete_combo)

        #à modifier avce les values du canvas
        info_layout = QHBoxLayout()
        self.__pourcentage_brun_initial = 0
        self.__pourcentage_combo_initial = 0
        self.__pourcentage_bleu_initial = 0
        self.__population_initial = 0
        self.__brun_pourcentage = QLabel('Brun 33%')
        self.__combo_pourcentage = QLabel('Combo 33%')
        self.__bleu_pourcentage = QLabel('Bleu 34%')
        self.__pop_total = QLabel('pop total: 900')
        
        self.__brun_pourcentage.set_fixed_width(100)
        self.__combo_pourcentage.set_fixed_width(100)
        self.__bleu_pourcentage.set_fixed_width(100)
        self.__pop_total.set_fixed_width(100)
        
        info_layout.add_widget(self.__brun_pourcentage)
        info_layout.add_widget(self.__combo_pourcentage)
        info_layout.add_widget(self.__bleu_pourcentage)
        info_layout.add_widget(self.__pop_total)
        
        param_layout.add_row('Information: ', info_layout)
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
        self.__population_bleu  = self._value_pop_bleu_sb.value
        self.update_population_initial()
 
    @Slot()
    def update_purete_brun(self):
        self.__population_brun  = self._value_pop_brun_sb.value
        self.update_population_initial()

    @Slot()
    def update_purete_combo(self):
        self.__population_combo  = self._value_pop_combo_sb.value
        self.update_population_initial()
        
    def update_population_initial(self):
        self.__population_initial = self.__population_brun + self.__population_combo + self.__population_bleu
        self.__pourcentage_brun_initial = self.__population_brun/self.__population_initial*100
        self.__pourcentage_combo_initial = self.__population_combo/self.__population_initial*100
        self.__pourcentage_bleu_initial  = self.__population_bleu/self.__population_initial*100
        
        self.update_yeux(self.__brun_pourcentage, self.__pourcentage_brun_initial, "Brun")
        self.update_yeux(self.__combo_pourcentage, self.__pourcentage_combo_initial, "Combo")
        self.update_yeux(self.__bleu_pourcentage, self.__pourcentage_bleu_initial, "Bleu")

        self.__pop_total.text = str(self.__population_initial)+" Individus"
        
    def update_yeux(self, label, pourcentage, nom):
        label.text = nom+": "+str(round(pourcentage,2))+"%"

    
    @property
    def problem_definition(self) -> ProblemDefinition:
        """Retourne la définition du problème.
        La définition du problème inclu les domaines des chromosomes et la fonction objective."""
        domains = Domains(np.array([[0.01,0.99],[0.01,0.99], [0.01,0.99]]),('Purete_brun','Purete_combo', 'Purete_bleu',))
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

    def _draw_chart(self,painter,solution,position, index):
        x,y,width,height = position
        painter.save()
        painter.set_brush(QColor(0,0,0))
        outer_rect = QRectF(x,y,width,height)
        painter.draw_rect(outer_rect)
        
        inner_width = outer_rect.width() / 3
        inner_height = outer_rect.height()
        
        for i in range(3):
            painter.set_brush(self.__colors[i])
            inner_rect = QRectF(outer_rect.left() + i * inner_width, outer_rect.top(), inner_width, inner_height * (solution[i]))
            painter.draw_rect(inner_rect)
        
        if index == 0:
            yellow_pen = QPen(QColor(255, 255, 0)) 
            yellow_pen.set_width(10)  
            painter.set_brush(Qt.NoBrush)
            painter.set_pen(yellow_pen)
            painter.draw_rect(outer_rect)

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
            self._draw_chart(painter,sorted_results[i],(col * squareWidth,
                                                        row * squareHeight,
                                                        squareWidth,
                                                        squareHeight), i)
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        
        painter.restore()
        pass


    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:
        size =  QSize(1500,1500)
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        painter.set_pen(Qt.NoPen)
        painter.set_brush(QColor(255, 255, 255))
        painter.draw_rect(self.__canvas)
        
        
        self._visualization_widget.image = image
        self._box_visualization_ratio = 0.9
        
        if np.size(self.__results)>0:
            self._draw_charts_grid(painter,size)
            
        painter.end()
        

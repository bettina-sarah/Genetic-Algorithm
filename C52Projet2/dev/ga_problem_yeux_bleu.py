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
        
        self.__population = 900
        self.__taux_croissance = 4
        self.__annee = 20

        # self.__population_brun = 0.85
        # self.__population_combo = 0.07
        # self.__population_bleu = 0.08
        
        # self.__probabilites_procreation = np.array([[4, 1, 0, 0, 0, 2],
        #                                             [0, 2, 0, 2, 4, 2],
        #                                             [0, 1, 4, 2, 0, 0 ]],dtype=np.float32)
                
        self.__probabilites_procreation = np.array([[1, 0.25, 0, 0, 0, 0.5],
                                                    [0, 0.5, 0, 0.5, 1, 0.5],
                                                    [0, 0.25, 1, 0.5, 0, 0 ]],dtype=np.float32)
        #premiere rangée = la valeur decimal de l'array reste converti en nombre binaire
        #deuxieme rangée = l'index du couple combo dans l'array couples_finales
        self.__lookup_table_reste = np.array([[5, 3, 6,],
                                              [4, 3, 5]],dtype=np.uint8)
        # ajouté: brun + bleu = 100% combo; 0% brun et 0% bleu
        self.__population_brun = 100
        self.__population_combo = 100
        self.__population_bleu  = 100
        
        
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

        self.__results = np.vstack((self.__results, pop_yeux))
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
        param_layout.add_row('Population bleu:', pop_bleu_layout)
        param_layout.add_row('Population brun:', pop_brun_layout)
        param_layout.add_row('Population combo:', pop_combo_layout)
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        #visualization
        visualization_group_box = QGroupBox('Visualization')
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._visualization_layout = QGridLayout(visualization_group_box)
        
        # chartView.set_render_hint(QPainter.Antialiasing)
        self._visualization_layout.add_widget(self.__chart_view)
        
        centre_layout.add_widget(param_group_box)
        centre_layout.add_widget(visualization_group_box)
        pass
    
    @Slot()
    def update_purete_bleu(self):
        self.__population_bleu  = self._value_pop_bleu_sb.value
  
    @Slot()
    def update_purete_brun(self):
        self.__population_brun  = self._value_pop_brun_sb.value

    @Slot()
    def update_purete_combo(self):
        self.__population_combo  = self._value_pop_combo_sb.value

    
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

    def _draw_charts(self):
        indexes = np.argsort(self.__scores, axis=0)[::-1]
        sorted_results = self.__results[indexes]
        
        # Data
        series = QBarSeries()
        categories = ["Best"]
        
        for i in range(len(sorted_results)):
            set = QBarSet("PopBrun")
            set << int(sorted_results[i,0])  
            set1 = QBarSet("PopCombo") 
            set1 << int(sorted_results[i,1])
            set2 = QBarSet("PopCombo")
            set2 << int(sorted_results[i,2])
            categories.append(str(i))

        series.append(set)
        series.append(set1)
        series.append(set2)
        # Chart
        chart = QChart()
        chart.add_series(series)
        chart.title = "Stacked Bar Chart Example"

        # X-axis
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.add_axis(axisX, Qt.AlignBottom)
        series.attach_axis(axisX)

        # Y-axis
        chart.create_default_axes()
        axis_y = chart.axes(Qt.Vertical)[0]
        chart.add_axis(axis_y, Qt.AlignLeft)

        # Chart view
        self.__chart_view.set_chart(chart)
        

    def _update_from_simulation(self, ga : GeneticAlgorithm | None) -> None:
        # if np.size(self.__results)>0:
        #     self._draw_charts()
        pass


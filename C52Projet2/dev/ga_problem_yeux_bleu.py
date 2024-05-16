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
        
        self.__population = 100
        self.__taux_croissance = 10
        self.__annee = 25

        self.__population_brun = 0.38
        self.__population_combo = 0.31
        self.__population_bleu = 0.31
        
        
        self.__probabilites_procreation = np.array([[1, 0.25, 0, 0, 0, 0.5],
                                                    [0, 0.5, 0, 0.5, 1, 0.5],
                                                    [0, 0.25, 1, 0.5, 0, 0 ]],dtype=np.float32)
        #premiere rangée = la valeur decimal de l'array reste converti en nombre binaire
        #deuxieme rangée = l'index du couple combo dans l'array couples_finales
        self.__lookup_table_reste = np.array([[5, 3, 6,],
                                              [4, 3, 5]],dtype=np.uint8)
        # ajouté: brun + bleu = 100% combo; 0% brun et 0% bleu
        self.__pop_bleu = 30
        self.__pop_brun = 30
        self.__pop_combo = 30
        
        
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
        
        chromosome = np.array([0.3,0.5,0.8])
        #conversion % choisis par le user en nbr int de personnes en fonc de population
        
        pop_brun = self.__population * self.__population_brun
        pop_combo = self.__population * self.__population_combo
        pop_bleu = self.__population * self.__population_bleu
        
        pop_gen = self.__population
        for _ in range(self.__annee):
            pop_yeux = np.array([pop_brun, pop_combo, pop_bleu], dtype=np.uint8)
            
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
            
            
             # ----- technique arrange bizzare -----------------------------
            # index combos dans couples_finales:
            #bleu-combo (3), brun-bleu (4), brun-combo (5)
            # arange = (0,1,2)
            # reste = 1, 1, 0 mettons, on veut savoir lequels a coupler;
            # np sum ici peut donner comme possibilités: 0+1 qui donne index 6 , ou 1+2 qui donne index 4, ou 0+2 qui donne index 5
            # dans array finale couples_finales
            # index_reste = np.sum(np.arange(3)[reste > 0])
            # couples_finales[-index_reste] = couples_finales[-index_reste] + 1 
            # --------------------------------------------------------------
            reste = [1,1,0]
            if np.sum(reste) > 0:
                # convertie l'array reste(un array binaire) en sa valeur decimal
                decimal_number = np.packbits(np.flip(reste), bitorder='little')
            
                # np where retourne tuple avec array: [index ou la comparaison est vraie, type de variable]
                index_lookup = np.where(self.__lookup_table_reste[0] == decimal_number[0])[0][0]
                
                index_combo = self.__lookup_table_reste[1, index_lookup]
                couples_finales[index_combo] = couples_finales[index_combo] + 1 
            # ---------------------------------------------
            # ajoute les couples avec le taux de croissance
            #couples = couples + self.croissance_couples()
            # trouve la nouvelle distribution de population
            
            pop_final = (couples_finales  * self.__probabilites_procreation)*2
            pop_final = np.array(np.sum(pop_final, axis=1), dtype=np.uint16)
            # update le nombre total de population
            pop_gen = np.sum(couples_finales)*2
            # ajouter le surplus au combo_brun (un surplus arrive lorsque *__probabilites_procreation donne un .5, mais l'array est en int)
            reste = pop_gen - np.sum(pop_final)
            pop_final[1] += reste # ajouter reste au combo
            pop_yeux = pop_final
            
           

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

        return score
    
    
    # def match_bleu(self,pop_yeux):
    #     # pop_bleu = pop_yeux[2]
    #     # pop_combo = pop_yeux[1]
        
    #     #trouve le restant bleu
    #     restant_bleu = pop_yeux[2] % 2
    #     #retire de la population des combos le restant des bleus (0 ou 1)
        
    #     #accouple tout les bleus ensemble, garde un pourcentage (préférence)
    #     # couple_bleu_bleu = math.floor(((pop_yeux[2] - restant_bleu) / 2) * self.__preference)
    #     couple_bleu_bleu = (pop_yeux[2] - restant_bleu)/2
        
        
    #     if couple_bleu_bleu % 2:
    #         couple_bleu_bleu *= self.__preference
    #         couple_bleu_bleu = math.floor(couple_bleu_bleu)
    #         # pop_yeux[2]+=2
    #     else:
    #         couple_bleu_bleu *= self.__preference
            
    #     # couple_bleu_bleu = math.floor(couple_bleu_bleu)
    #     #retire de la population bleus le nombre qui s'est acoouplé
    #     pop_yeux[2] -= couple_bleu_bleu * 2
    #     #le couple combo_bleu = restant (0,1)
    #     couple_combo_bleu = pop_yeux[2]
    #     pop_yeux[2] -= couple_combo_bleu
    #     pop_yeux[1] -= couple_combo_bleu
        
    #     return couple_bleu_bleu , couple_combo_bleu
    
    # def match_brun(self,pop_yeux):
    #     # brun =  pop_yeux[0]
    #     # combo = pop_yeux[1]
    #     couples_brun_combo = min(pop_yeux[0],  pop_yeux[1])
    #     pop_yeux[0] -= couples_brun_combo
    #     pop_yeux[1] -= couples_brun_combo
        
    #     return couples_brun_combo
    
    # # utiliser pour match final sur pop_brun et pop_combo
    # def match_couple_final(self, pop_yeux, yeux):
    #     couples = pop_yeux[yeux] / 2
    #     pop_yeux[yeux] -= couples * 2
    #     return couples
    
    
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
        
        # chartView.set_render_hint(QPainter.Antialiasing)
        self._visualization_layout.add_widget(self.__chart_view)
        
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


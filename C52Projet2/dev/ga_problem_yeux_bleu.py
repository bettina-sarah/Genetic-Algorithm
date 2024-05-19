import numpy as np
from numpy.typing import NDArray
import math
import random

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtgui import process_area
from uqtwidgets import QImageViewer, create_scroll_int_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QPixmap
from PySide6.QtCore import Slot, Qt, QSize, QRectF

from __feature__ import snake_case, true_property

class QEyeProblemPanel(QSolutionToSolvePanel):
    
    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
    
        self.display_panel()
        
        self.__canvas = QRectF(0,0,1500,500)
        self.__annee = 20

                
        self.__probabilites_procreation = np.array([[1, 0.25, 0, 0, 0, 0.5],
                                                    [0, 0.5, 0, 0.5, 1, 0.5],
                                                    [0, 0.25, 1, 0.5, 0, 0 ]],dtype=np.float32)
        
        #premiere rangée = la valeur decimal de l'array 'reste' converti en nombre binaire
        #deuxieme rangée = l'index du couple combo dans l'array 'couples_finales' 
        self.__lookup_table_reste = np.array([[5, 3, 6,],
                                              [4, 3, 5]],dtype=np.uint8)
        
        self.__population_brun  = self._value_pop_brun_sb.value
        self.__population_combo  = self._value_pop_combo_sb.value
        self.__population_bleu   = self._value_pop_bleu_sb.value
        
        self.__colors = (QColor(0,0,255),
                         QColor(245,213,162),
                         QColor(165,42,42))
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        self.__results_pourcentage = np.empty((0,3),dtype=np.float64)
        

    @property
    def unknown_value(self) -> float:
        """La valeur recherchée par l'algorithme génétique."""
        return self._value_scroll_bar.get_real_value()

    @property
    def name(self) -> str: # note : override
        return 'Problème d’optimisation de pureté de couple dans une population'

    @property
    def summary(self) -> str: # note : override
        return '''On cherche à trouver la balance parfaite des taux de pureté de couple permettant d'obtenir une balance entre les trois pairs de couleurs de yeux possible après un certain nombre d'année'''

    @property
    def description(self) -> str: # note : override
        return '''On cherche à trouver les taux de pureté de couple néccessaire pour obtenir ce qui se rapproche le plus d'une balance de population entre les 3 paires de yeux après qu'un certain nombre d'année ai passé'''

    @property
    def pop_brun(self):
        return self.__population_brun
    
    @pop_brun.setter
    def pop_brun(self, value):
        self.__population_brun = value

    @property
    def pop_combo(self):
        return self.__population_combo
    
    @pop_combo.setter
    def pop_combo(self, value):
        self.__population_combo = value

    @property
    def pop_bleu(self):
        return self.__population_bleu
    
    @pop_bleu.setter
    def pop_bleu(self, value):
        self.__population_bleu = value


    def __call__(self, chromosome : NDArray) -> float:
        """Retourne le volume de la boîte obtenue en fonction de la taille de la découpe."""
        
        pop_gen = self.pop_brun + self.pop_combo + self.pop_bleu
        
        # commence avec une population paire
        r = pop_gen % 2
        pop_gen += r
        self.pop_combo += r
        
        pop_yeux = np.array([self.pop_brun, self.pop_combo, self.pop_bleu], dtype=np.uint32)
        for _ in range(self.__annee):
            # pop_yeux = np.array([pop_brun, pop_combo, pop_bleu], dtype=np.uint8)
            couples_finales = np.zeros(6, dtype=np.uint16)
            
            #retirer les impaires
            reste = pop_yeux % 2
            pop_yeux = pop_yeux - reste
            # faire couples  et apres, couples pures avec % purete; dtype assure le math.floor
            couples = pop_yeux / 2
            couples_pures = np.array(couples * chromosome, dtype=np.uint16)
            couples_finales[:3] = couples_pures
            
            # revenir avec la population non accouplé
            couples = couples - couples_pures
            pop_yeux = couples * 2

            # couples mixtes:
            # 1- sort la population restante en odre du plus petit au plus grand restant
            # 2- la couleur de yeux la plus petites sera divisé en 2 et accouplé avec les 2 autres couleurs restantes
            # 3- la couleur de yeux suivant la plus petite sera accouplé au complet avec la couleure restante
            # 4- la couleur avec le plus grand nombre d'individus pourrait avoir personne avec qui s'accomplé, elle s'accomplera avec elle-meme dans ce cas 
            couples_combo = np.zeros(3, dtype=np.uint16)
            
            #1.
            sorted_pop_yeux = np.argsort(pop_yeux)
            premiere_couleur = sorted_pop_yeux[0]
            deuxieme_couleur = sorted_pop_yeux[1]
            troisieme_couleur = sorted_pop_yeux[2]

            #2.
            mask = pop_yeux != pop_yeux[premiere_couleur]
            nouveaux_couples_mixtes = pop_yeux[premiere_couleur]/2
            pop_yeux[mask] = pop_yeux[mask] - nouveaux_couples_mixtes
            couples_combo[mask] = nouveaux_couples_mixtes
            pop_yeux[premiere_couleur] = 0
            couples_combo[premiere_couleur] = pop_yeux[deuxieme_couleur]

            #3.
            pop_yeux[mask] = pop_yeux[mask] - pop_yeux[deuxieme_couleur]
            pop_yeux[deuxieme_couleur] = 0
            
            #4.
            couples_finales[troisieme_couleur] = couples_finales[troisieme_couleur] + pop_yeux[troisieme_couleur] / 2
    
            couples_finales[3:] = couples_combo
            
            # les restants (ceux retiré pour avoir des chiffres paires)
            # le tableau sera soit [0,0,0] soit une combinaison [1,1,0], [1,0,1], [0,1,1]
            # 1. trouver la valeur décimal de chaque combinaison
            # 2. à l'aide de la table '__lookup_table_reste' chaque valeur décimal est lié à l'index d'un couple combo de la table couples_finales
            # 3. ajoute 1 couple à l'index trouvé 
            if np.sum(reste) > 0:
                decimal_number = np.packbits(np.flip(reste), bitorder='little')
                index_lookup = np.where(self.__lookup_table_reste[0] == decimal_number[0])[0][0]
                index_combo = self.__lookup_table_reste[1, index_lookup]
                couples_finales[index_combo] = couples_finales[index_combo] + 1 

            # multiplie les couples à la charte de probabiltes, *2 pour avoir la nouvelle pop
            pop_final = (couples_finales  * self.__probabilites_procreation)*2
            # trouve la somme pour chaque couleur
            pop_final = np.array(np.sum(pop_final, axis=1), dtype=np.uint16)

            # un surplus arrive lorsque *__probabilites_procreation donne un .5, mais l'array est en int
            # on redistribue les individues perdu aux yeux combos
            reste = pop_gen - np.sum(pop_final)
            pop_final[1] += reste
            pop_yeux = pop_final
            pop_gen = np.sum(pop_final)
    

        pourcentage_bleu = pop_yeux[2]/pop_gen  
        pourcentage_brun = pop_yeux[0]/pop_gen
        pourcentage_combo = pop_yeux[1]/pop_gen

        score = ((pourcentage_bleu-0.33)**2 + (pourcentage_brun - 0.33)**2 + (pourcentage_combo-0.33)**2)**0.5
        score = 1 - score

        liste_pourcentages_yeux = np.array([pourcentage_bleu * 100,pourcentage_brun * 100,pourcentage_combo * 100],dtype=np.float64)
        self.__results_pourcentage = np.vstack((self.__results_pourcentage, liste_pourcentages_yeux))
        self.__results = np.vstack((self.__results, chromosome))
        self.__scores = np.append(self.__scores, score)
        return score
     
    def display_panel(self):
        
        centre_layout = QVBoxLayout(self)
        #param
        param_group_box = QGroupBox('Informations')
        param_layout = QFormLayout(param_group_box)

        self._value_pop_bleu_sb, pop_bleu_layout = create_scroll_int_value(100,500,1000,"")
        self._value_pop_brun_sb, pop_brun_layout = create_scroll_int_value(100,500,1000,"")
        self._value_pop_combo_sb, pop_combo_layout = create_scroll_int_value(100,500,1000,"")
        
        self._value_pop_bleu_sb.valueChanged.connect(self.update_purete_bleu)
        self._value_pop_brun_sb.valueChanged.connect(self.update_purete_brun)
        self._value_pop_combo_sb.valueChanged.connect(self.update_purete_combo)

        #à modifier avce les values du canvas
        
        self.__color_mapping = {
                (0, 10): (128,0,0),
                (10, 20): (178,34,34),   
                (20, 30): (255,0,0),  
                (30, 40): (255,140,0), 
                (40, 50): (255,215,0),  
                (50, 60): (173,255,47), 
                (60, 70): (50,205,50),  
                (70, 80): (60,179,113), 
                (80, 90): (34,139,34),
                (90, 100): (128,128,0)}
        
        icon_size = 15
        info_layout = QHBoxLayout()

        # DONT REPEAT YOURSELF LMFAO <---------------------------------- 
        self.__pourcentage_brun_initial = 0
        self.__pourcentage_combo_initial = 0
        self.__pourcentage_bleu_initial = 0
        self.__population_initial = 0
        self.__brun_icon = QLabel()
        self.__brun_icon.set_fixed_width(icon_size)
        self.__brun_icon.set_fixed_height(icon_size)
        self.__brun_pourcentage = QLabel('Brun 33%')
        self.__combo_icon = QLabel()
        self.__combo_icon.set_fixed_width(icon_size)
        self.__combo_icon.set_fixed_height(icon_size)
        self.__combo_pourcentage = QLabel('Combo 33%')
        self.__bleu_icon = QLabel()
        self.__bleu_icon.set_fixed_width(icon_size)
        self.__bleu_icon.set_fixed_height(icon_size)
        self.__bleu_pourcentage = QLabel('Bleu 34%')
        self.__pop_total = QLabel('pop total: 900')
        
        self.__brun_pourcentage.set_fixed_width(100)
        self.__combo_pourcentage.set_fixed_width(100)
        self.__bleu_pourcentage.set_fixed_width(100)

        # DONT REPEAT YOURSELF LMFAO <----------------------------------
        self.__pop_total.set_fixed_width(100)
        
        info_layout.add_widget(self.__brun_icon)
        info_layout.add_widget(self.__brun_pourcentage)
        info_layout.add_widget(self.__combo_icon)
        info_layout.add_widget(self.__combo_pourcentage)
        info_layout.add_widget(self.__bleu_icon)
        info_layout.add_widget(self.__bleu_pourcentage)
        info_layout.add_widget(self.__pop_total)
        
        param_layout.add_row('Information: ', info_layout)
        param_layout.add_row('Population brun:', pop_brun_layout)
        param_layout.add_row('Population combo:', pop_combo_layout)
        param_layout.add_row('Population bleu:', pop_bleu_layout)
        
        param_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        #visualization
        visualization_group_box = QGroupBox('Visualization')
        visualization_group_box.size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._visualization_layout = QGridLayout(visualization_group_box)
        self._visualization_widget = QImageViewer(True)
        self._visualization_layout.add_widget(self._visualization_widget)

        # DONT REPEAT YOURSELF LMFAO <----------------------------------

        # DONT REPEAT YOURSELF LMFAO <----------------------------------
        #Meilleurs pourcentages display
        meilleurs_pourcentages = QGroupBox()
        meilleurs_pourcentages.resize(100,5)
        pourcentages_pop_meilleure_solution = QHBoxLayout()
        self.__pourcentage_brun_final = QLabel()
        pourcentages_pop_meilleure_solution.add_widget(self.__pourcentage_brun_final)
        self.__pourcentage_combo_final = QLabel()
        pourcentages_pop_meilleure_solution.add_widget(self.__pourcentage_combo_final)
        self.__pourcentage_bleu_final = QLabel()
        pourcentages_pop_meilleure_solution.add_widget(self.__pourcentage_bleu_final)
        meilleurs_pourcentages.set_layout(pourcentages_pop_meilleure_solution)
        param_layout.add_row("Pourcentages: ", meilleurs_pourcentages)

        # DONT REPEAT YOURSELF LMFAO <----------------------------------

        centre_layout.add_widget(param_group_box)
        # centre_layout.add_widget(meilleurs_pourcentages)
        centre_layout.add_widget(visualization_group_box)
        pass
    
    @Slot()
    def update_purete_bleu(self):
        self.pop_bleu  = self._value_pop_bleu_sb.value
        self.__update_population_initial()
 
    @Slot()
    def update_purete_brun(self):
        self.pop_brun  = self._value_pop_brun_sb.value
        self.__update_population_initial()

    @Slot()
    def update_purete_combo(self):
        self.pop_combo  = self._value_pop_combo_sb.value
        self.__update_population_initial()
        
    def __update_population_initial(self):
        self.__population_initial = self.__population_brun + self.__population_combo + self.__population_bleu
        self.__pourcentage_brun_initial = self.__population_brun/self.__population_initial*100
        self.__pourcentage_combo_initial = self.__population_combo/self.__population_initial*100
        self.__pourcentage_bleu_initial  = self.__population_bleu/self.__population_initial*100
        
        self.__update_yeux(self.__brun_pourcentage,self.__brun_icon ,self.__pourcentage_brun_initial, "Brun")
        self.__update_yeux(self.__combo_pourcentage,self.__combo_icon, self.__pourcentage_combo_initial, "Combo")
        self.__update_yeux(self.__bleu_pourcentage, self.__bleu_icon, self.__pourcentage_bleu_initial, "Bleu")

        self.__pop_total.text = str(self.__population_initial)+" Individus"
        
    def __update_yeux(self, label, icon, pourcentage, nom):
        label.text = nom+": "+str(round(pourcentage,2))+"%"
        self.__set_icon(icon, pourcentage)
        

    def __set_icon(self, label, percentage):
        pixmap = QPixmap(label.size)
        
        for key in self.__color_mapping:
            if key[0] <= percentage < key[1]:
                r, g, b = self.__color_mapping[key]
                pixmap.fill(QColor(r, g, b))
    
        label.pixmap = pixmap

    
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
            inner_rect = QRectF(outer_rect.left() + i * inner_width, outer_rect.bottom() - inner_height * (solution[i]), inner_width, inner_height * (solution[i]))
            painter.draw_rect(inner_rect)
        
        if index == 0:
            yellow_pen = QPen(QColor(255, 255, 0)) 
            yellow_pen.set_width(20)
            painter.set_brush(Qt.NoBrush)
            painter.set_pen(yellow_pen)
            painter.draw_rect(outer_rect)

        painter.restore()
        pass
         
    def _draw_charts_grid(self,painter,size, sorted_results):
        painter.save()
        
        
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
            if i == cells_quantity - 1 and not cells_pair:
                 break

            row = i // cols
            col = i % cols
            self._draw_chart(painter,sorted_results[i],(col * squareWidth,
                                                        row * squareHeight,
                                                        squareWidth,
                                                        squareHeight), i)
        
        self.__results = np.empty((0,3),dtype=np.float32)
        self.__scores = np.empty(0,dtype=np.float32)
        self.__results_pourcentage = np.empty((0,3),dtype=np.float64)
        
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
            indexes = np.argsort(self.__scores, axis=0)[::-1]
            sorted_results = self.__results[indexes]
            sorted_results_pourcentage = self.__results_pourcentage[indexes]
            self._draw_charts_grid(painter,size, sorted_results)
            painter.end()
            self.__pourcentage_bleu_final.text = "% Bleus: " + str(round(sorted_results_pourcentage[0][0],2))
            self.__pourcentage_brun_final.text = "% Bruns: " + str(round(sorted_results_pourcentage[0][1],2))
            self.__pourcentage_combo_final.text = "% Combos: " + str(round(sorted_results_pourcentage[0][2],2))
        else:
            painter.end()

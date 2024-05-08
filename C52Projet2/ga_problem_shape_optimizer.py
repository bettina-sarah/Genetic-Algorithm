import numpy as np
from numpy.typing import NDArray

from gacvm import Domains, ProblemDefinition, Parameters, GeneticAlgorithm
from gaapp import QSolutionToSolvePanel

from uqtwidgets import QImageViewer, create_scroll_real_value

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtGui import QImage, QPainter, QColor, QPolygonF, QPen, QBrush, QFont
from PySide6.QtCore import Slot, Qt, QSize, QPointF, QRectF, QSizeF

from __feature__ import snake_case, true_property

class QOpenBoxProblemPanel(QSolutionToSolvePanel):
    """Panel to solve the open box problem."""

    def __init__(self, width : int = 10., height : int = 5., parent : QWidget | None = None) -> None:
        super().__init__(parent)
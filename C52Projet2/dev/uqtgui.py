#     ___  _    ____       _         _   _ _ _ _   _           
#    / _ \| |_ / ___|_   _(_)  _   _| |_(_) (_) |_(_) ___  ___ 
#   | | | | __| |  _| | | | | | | | | __| | | | __| |/ _ \/ __|
#   | |_| | |_| |_| | |_| | | | |_| | |_| | | | |_| |  __/\__ \
#    \__\_\\__|\____|\__,_|_|  \__,_|\__|_|_|_|\__|_|\___||___/
#                                                              


import math
import umath

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPolygonF, QVector2D
from __feature__ import snake_case, true_property



# def perimeter_from_QRectF(rect):
#     return 2. * (rect.width() + rect.height())

# def area_from_QRectF(rect):
#     return rect.width() * rect.height()

# def perimeter_from_QPolygonF(polygon):
#     perimeter = 0.
#     prev_index = polygon.size() - 1
#     for cur_index in range(polygon.size()):
#         perimeter += QVector2D(polygon[cur_index] - polygon[prev_index]).length()
#         prev_index = cur_index
#     return perimeter

# def area_from_QPolygonF(polygon):
#     area = 0.
#     prev_index = polygon.size() - 1
#     for cur_index in range(polygon.size()):
#         area += (polygon[cur_index].x() - polygon[prev_index].x()) * (polygon[cur_index].y() + polygon[prev_index].y()) / 2.0; # trapezoidal integration around the shape
#         prev_index = cur_index
#     return abs(area)


def process_perimeter(rect_or_polygon):
    if isinstance(rect_or_polygon, QRectF):
        return 2. * (rect_or_polygon.width() + rect_or_polygon.height())
    elif isinstance(rect_or_polygon, QPolygonF):
        perimeter = 0.
        prev_index = rect_or_polygon.size() - 1
        for cur_index in range(rect_or_polygon.size()):
            perimeter += QVector2D(rect_or_polygon[cur_index] - rect_or_polygon[prev_index]).length()
            prev_index = cur_index
        return perimeter
    else:
        raise TypeError(f'process_perimeter() expects a QRectF or a QPolygonF, not a {type(rect_or_polygon)}')

def process_area(rect_or_polygon):
    if isinstance(rect_or_polygon, QRectF):
        return rect_or_polygon.width() * rect_or_polygon.height()
    elif isinstance(rect_or_polygon, QPolygonF):
        area = 0.
        prev_index = rect_or_polygon.size() - 1
        for cur_index in range(rect_or_polygon.size()):
            area += (rect_or_polygon[cur_index].x() - rect_or_polygon[prev_index].x()) * (rect_or_polygon[cur_index].y() + rect_or_polygon[prev_index].y()) / 2.0; # trapezoidal integration around the shape
            prev_index = cur_index
        return abs(area)
    else:
        raise TypeError(f'process_area() expects a QRectF or a QPolygonF, not a {type(rect_or_polygon)}')




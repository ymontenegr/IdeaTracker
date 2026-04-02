#!/usr/bin/env python3
"""
Genera assets/IdeaTracker.png (256x256) a partir del SVG.
Se ejecuta una sola vez durante la instalación o el build.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QImage

app = QApplication.instance() or QApplication(sys.argv)

SVG_PATH = os.path.join(os.path.dirname(__file__), "assets", "IdeaTracker.svg")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "assets", "IdeaTracker.png")

def svg_to_png(svg_path: str, out_path: str, size: int = 256):
    renderer = QSvgRenderer(svg_path)
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    image.save(out_path, "PNG")
    print(f"Ícono generado: {out_path}  ({size}x{size} px)")

svg_to_png(SVG_PATH, OUT_PATH, 256)

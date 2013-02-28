#!/usr/bin/env python

"""
colourpalette.py - Display thread colours in a palette widget.

Copyright (C) 2009 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os, sys
from PyQt4.QtCore import QLine, QObject, QPoint, QRect, QSize, Qt, QVariant, \
                         SIGNAL, SLOT
from PyQt4.QtGui import *

import colourmodels


class ColourPalette(QDialog):

    def __init__(self, parent = None):
    
        QDialog.__init__(self, parent)
        
        self.colourView = QTableView()
        self.colourModel = colourmodels.ColourModel()
        self.colourView.setModel(self.colourModel)
        self.colourView.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.connect(self.colourView, SIGNAL("activated()"), self.accept)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"), self.reject)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.colourView)
        layout.addWidget(buttonBox)
        
        self.setWindowTitle(self.tr("Colour Palette"))
    
    def exec_(self, item):
    
        index = self.colourModel.getIndex(item.internalColour(), item.threadType())
        
        self.colourView.selectionModel().setCurrentIndex(index,
            QItemSelectionModel.ClearAndSelect)
        
        self.colourView.setFocus(Qt.ActiveWindowFocusReason)
        return QDialog.exec_(self)
    
    def selectedInternalColour(self):
    
        index = self.colourView.selectionModel().currentIndex()
        if index.isValid():
            return self.colourModel.internalColour(index)
        else:
            return None
    
    def selectedThreadType(self):
    
        index = self.colourView.selectionModel().currentIndex()
        if index.isValid():
            return self.colourModel.threadType(index)
        else:
            return None

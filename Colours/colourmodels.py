#!/usr/bin/env python

"""
jefviewer.py - Display the contents of JEF files.

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
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, \
                         SIGNAL, SLOT
from PyQt4.QtGui import *

import jef_colours

class PatternColourItem(QStandardItem):

    def __init__(self, internal_colour):
    
        QStandardItem.__init__(self)
        
        self.internal_colour = internal_colour
        self._colours = jef_colours.colour_mappings[internal_colour]
        
        for thread_type in jef_colours.colour_groups:
            if self._colours.has_key(thread_type):
                self.thread_type = thread_type
                break
        else:
            # We should never have an undefined thread type.
            self.thread_type = None
        
        self.setColour(internal_colour, self.thread_type)
    
    def colour(self):
    
        code = self._colours[self.thread_type]
        name, colour = jef_colours.known_colours[self.thread_type][code]
        return colour
    
    def internalColour(self):
    
        return self.internal_colour
    
    def threadType(self):
    
        return self.thread_type
    
    def isChecked(self):
    
        return self.checkState() == Qt.Checked
    
    def setColour(self, internal_colour, thread_type):
    
        self.internal_colour = internal_colour
        self.thread_type = thread_type
        self._colours = jef_colours.colour_mappings[internal_colour]
        
        code = self._colours[thread_type]
        name, colour = jef_colours.known_colours[thread_type][code]
        
        self.setText(QApplication.translate("PatternColourItem", "%1: %2 (%3)").arg(code).arg(name, thread_type))
        self.setData(QVariant(QColor(colour)), Qt.DecorationRole)
        self.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)


class PatternColourModel(QStandardItemModel):

    def __init__(self, background):
    
        QStandardItemModel.__init__(self)
        
        self.background = background
        self.pattern = None
        
        self.connect(self, SIGNAL("itemChanged(QStandardItem *)"),
                     self, SIGNAL("colourChanged()"))
        self.connect(self, SIGNAL("itemChanged(QStandardItem *)"),
                     self.updatePattern)
    
    def setBackground(self, colour):
    
        self.background = colour
        self.emit(SIGNAL("backgroundChanged()"))
    
    def setPattern(self, pattern):
    
        self.pattern = pattern
        
        # Update the colours in the list with those from the pattern.
        self.clear()
        
        for internal_colour in pattern.colours:
        
            item = PatternColourItem(internal_colour)
            self.appendRow(item)
    
    def updatePattern(self, item):
    
        self.pattern.set_colour(item.row(), item.internalColour())


class ColourItem:

    """ColourItem
    
    Represents an internal Janome colour and its interpretations in different
    thread types.
    """
    
    def __init__(self, internal_colour):
    
        self.internal_colour = internal_colour
        self._colours = jef_colours.colour_mappings[internal_colour]
    
    def data(self, thread_type):
    
        code = self._colours[thread_type]
        return code
    
    def hasThread(self, thread_type):
    
        return self._colours.has_key(thread_type)
    
    def colour(self, thread_type = None):
    
        code = self.data(thread_type)
        name, colour = jef_colours.known_colours[thread_type][code]
        return colour
    
    def colours(self):
    
        return self._colours
    
    def name(self, thread_type = None):
    
        code = self.data(thread_type)
        name, colour = jef_colours.known_colours[thread_type][code]
        return name


class ColourModel(QAbstractTableModel):

    def __init__(self):
    
        QAbstractTableModel.__init__(self)
        
        self.connect(self, SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                     self, SIGNAL("colourChanged()"))
        
        # Create a list of rows for the model, each containing the thread
        # colours which correspond to a given internal colour.
        self.colours = []
        self.headers = list(jef_colours.colour_groups)
        
        keys = jef_colours.colour_mappings.keys()
        keys.sort()
        
        for internal_colour in keys:
        
            item = ColourItem(internal_colour)
            self.colours.append(item)
    
    def rowCount(self, parent):
    
        if parent.isValid():
            return -1
        else:
            return len(self.colours)
    
    def columnCount(self, parent):
    
        if parent.isValid():
            return -1
        else:
            return len(self.headers)
    
    def data(self, index, role):
    
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        if not 0 <= row < self.colours:
            return QVariant()
        
        item = self.colours[row]
        if not 0 <= index.column() < len(self.headers):
            return QVariant()
        
        thread_type = self.headers[index.column()]
        
        try:
            if role == Qt.DisplayRole:
                return QVariant(item.name(thread_type))
            elif role == Qt.DecorationRole:
                return QVariant(QColor(item.colour(thread_type)))
            else:
                return QVariant()
        except KeyError:
            return QVariant()
    
    def flags(self, index):
    
        if not index.isValid():
            return Qt.NoItemFlags
        
        item = self.colours[index.row()]
        thread_type = self.headers[index.column()]
        
        if item.hasThread(thread_type):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemFlags(Qt.ItemFlag(0)) # Qt.NoItemFlags
    
    def headerData(self, section, orientation, role):
    
        if role != Qt.DisplayRole:
            return QVariant()
        
        if orientation == Qt.Vertical:
            return QVariant(self.colours[section].internal_colour)
        else:
            return QVariant(self.headers[section])
    
    def internalColour(self, index):
    
        """Returns the internal colour of the item with the given index."""
        
        item = self.colours[index.row()]
        return item.internal_colour
    
    def threadType(self, index):
    
        """Returns the thread type of the colour represented by the given index."""
        return self.headers[index.column()]
    
    def getIndex(self, internal_colour, thread_type):
    
        row = 0
        for item in self.colours:
        
            if item.internal_colour == internal_colour:
            
                try:
                    column = self.headers.index(thread_type)
                    return self.createIndex(row, column)
                except ValueError:
                    return QModelIndex()
            
            row += 1
        
        return QModelIndex()

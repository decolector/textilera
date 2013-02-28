#!/usr/bin/env python

"""
svg2jef.py - Creates JEF files based on paths in SVG drawings.

Copyright (C) 2010 David Boddie <david@boddie.org.uk>

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
try:
    from PyQt4.QtXml import QXmlStreamReader
except ImportError:
    from PyQt4.QtCore import QXmlStreamReader

from PyQt4.QtCore import QCoreApplication

import jef
from Colours import jef_colours

class PathReader(QXmlStreamReader):

    Commands = {
        u"M": 2, u"m": 2,
        u"Z": 0, u"z": 0,
        u"L": 2, u"l": 2,
        u"H": 1, u"h": 1,
        u"V": 1, u"v": 1,
        u"C": 6, u"c": 6,
        u"S": 4, u"s": 4,
        }
    
    def __init__(self, path):
    
        QXmlStreamReader.__init__(self, open(path).read())
    
    def read(self):
    
        paths = []
        path = []
        
        while not self.atEnd():
        
            token = self.readNext()
            if token == self.StartElement:
            
                if self.name().toString() == u"path":
                
                    style = unicode(self.attributes().value(u"style").toString())
                    style_pieces = map(lambda x: x.strip(), style.split(u";"))
                    style_dict = dict(map(lambda x: x.split(u":"), style_pieces))
                    
                    data = unicode(self.attributes().value(u"d").toString())
                    new_paths = self._read_path(data)
                    paths += map(lambda path: (style_dict, path), new_paths)
        
        return paths
    
    def _read_path(self, data):
    
        paths = []
        path = []
        op = None
        args = []
        arg = u""
        arg_number = 0
        
        for c in data:
            if c in u"-0123456789.e":
                arg += c
            else:
                if arg:
                    args.append(float(arg))
                    arg = u""
                    if len(args) == arg_number:
                        path.append((op, args))
                        args = []
                
                if self.Commands.has_key(c):
                
                    if len(args) != 0 and len(args) != arg_number:
                        sys.stderr.write("Unexpected number of arguments in preceding command at line %i; column %i: '%s'\n" % (self.lineNumber(), self.columnNumber(), c))
                    
                    op = c
                    args = []
                    arg = u""
                    arg_number = self.Commands[c]
                elif c in u" \t\r\n,":
                    pass
                else:
                    sys.stderr.write("Unknown command in path at line %i; column %i: '%s'\n" % (self.lineNumber(), self.columnNumber(), c))
                
                if c == u"Z" or c == u"z":
                    if path:
                        paths.append(path)
                        path = []
        
        if arg:
            args.append(float(arg))
            arg = u""
            if len(args) == arg_number:
                path.append((op, args))
                args = []
        
        if path:
            paths.append(path)
        
        return paths


if __name__ == "__main__":

    if not 2 <= len(sys.argv) <= 4:
        sys.stderr.write("Usage: %s [maximum stitch length (JEF units)] <SVG file> <JEF file>\n" % sys.argv[0])
        sys.exit(1)
    
    elif len(sys.argv) == 4:
        max_stitch_length = min(max(1.0, float(sys.argv[1])), 127.0)
        svg_file = sys.argv[2]
        jef_file = sys.argv[3]
    
    else:
        max_stitch_length = 127.0
        svg_file = sys.argv[1]
        jef_file = sys.argv[2]
    
    app = QCoreApplication(sys.argv)
    
    reader = PathReader(svg_file)
    paths = reader.read()
    
    pattern = jef.Pattern()
    pattern.threads = len(paths)
    
    groups, known, default, mappings = jef_colours.read_colours()
    
    inverse_mappings = {}
    for internal_code, group_colour in mappings.items():
    
        for group, colour_code in group_colour.items():
            inverse_mappings[(group, colour_code)] = internal_code
    
    colours = {}
    for group in groups:
    
        if not known.has_key(group):
            continue
        
        for colour_code, (name, rgb) in known[group].items():
            if not colours.has_key(rgb):
                internal_code = inverse_mappings.get((group, colour_code), 2)
                colours[rgb] = internal_code
    
    cx, cy = 0, 0
    
    for style, path in paths:
    
        rgb = style.get(u"stroke", u"#000000").upper()
        internal_code = colours.get(rgb, 2)
        
        coordinates = []
        
        for op, args in path:
        
            if op == u"M":
                command = "move"
                x, y = args
            elif op == u"m":
                command = "move"
                x, y = args
                x += cx
                y += cy
            elif op == u"L":
                command = "stitch"
                x, y = args
            elif op == u"l":
                command = "stitch"
                x, y = args
                x += cx
                y += cy
            elif op == u"C":
                command = "stitch"
                x, y = args[-2:]
            elif op == u"c":
                command = "stitch"
                x, y = args[-2:]
                x += cx
                y += cy
            elif op == u"S":
                command = "stitch"
                x, y = args[-2:]
            elif op == u"s":
                command = "stitch"
                x, y = args[-2:]
                x += cx
                y += cy
            else:
                continue
            
            cx, cy = x, y
            # Store the coordinates using the pattern's coordinate system.
            coordinates.append((command, int(cx), int(-cy)))
        
        if coordinates:
            pattern.coordinates.append(coordinates)
            pattern.colours.append(internal_code)
            pattern.thread_types.append(13)
    
    
    # Translate the pattern to be centred about the origin.
    x1, y1, x2, y2 = pattern.bounding_rect()
    dx = -(x2 - x1)/2 - x1
    dy = -(y2 - y1)/2 - y1
    
    cx, cy = 0, 0
    
    for coordinates in pattern.coordinates:
    
        i = 0
        while i < len(coordinates):
        
            command, x, y = coordinates[i]
            x = int(x + dx)
            y = int(y + dy)
            
            # If one or both dimensions are greater than the maximum stitch
            # length then split the line into pieces.
            d = max(abs(x - cx), abs(y - cy))
            n = (d / max_stitch_length)
            
            if n > 1:
            
                xs = max(-max_stitch_length, min(float(x - cx)/n, max_stitch_length))
                ys = max(-max_stitch_length, min(float(y - cy)/n, max_stitch_length))
                
                # Insert moves/stitches at intermediate positions.
                j = 1
                while j < n:
                    px = cx + (j * xs)
                    py = cy + (j * ys)
                    coordinates.insert(i, (command, int(px), int(py)))
                    i += 1
                    j += 1
                
                cx, cy = px, py
            
            # Update the original coordinate.
            coordinates[i] = (command, x, y)
            cx, cy = x, y
            i += 1
    
    pattern.save(jef_file)
    
    sys.exit()

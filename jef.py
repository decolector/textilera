#!/usr/bin/env python

"""
jef.py - Read and write JEF files.

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

import struct, sys, time

from Colours import jef_colours

class Pattern:

    def __init__(self, path = None):
    
        if path:
            self.load(path)
        else:
            self.date_time = None
            self.threads = 0
            self.hoop_size = (126, 110)
            self.hoop_name = "A"
            self.rectangles = []
            self.colours = []
            self.thread_types = []
            self.coordinates = []
    
    def load(self, path):
    
        self._data = d = open(path).read()
        start = struct.unpack("<I", d[:4])[0]
        data = d[start:]
        
        self.date_time = None
        if struct.unpack("<I", d[4:8])[0] & 1:
            self.date_time = time.strptime(d[8:22], "%Y%m%d%H%M%S")
        
        self.threads = struct.unpack("<I", d[24:28])[0]
        data_length = struct.unpack("<I", d[28:32])[0] * 2
        
        # start + data_length should equal the file length.
        
        hoop_code = struct.unpack("<I", d[32:36])[0]
        
        # Determine the hoop size in millimetres.
        if hoop_code == 0:
            self.hoop_size = (126, 110)
            self.hoop_name = "A"
        elif hoop_code == 1:
            self.hoop_size = (50, 50)
            self.hoop_name = "C"
        elif hoop_code == 2:
            self.hoop_size = (140, 200)
            self.hoop_name = "B"
        elif hoop_code == 3:
            self.hoop_size = (126, 110)
            self.hoop_name = "F"
        elif hoop_code == 4:
            self.hoop_size = (230, 200)
            self.hoop_name = "D"
        else:
            self.hoop_size = None
            self.hoop_name = None
        
        # These are coordinates specifying rectangles for the pattern.
        # It appears that the units are 0.2 mm.
        self.rectangles = []
        offset = 0x24
        while offset < 0x74:
        
            x1 = struct.unpack("<i", d[offset:offset+4])[0]
            y1 = struct.unpack("<i", d[offset+4:offset+8])[0]
            x2 = struct.unpack("<i", d[offset+8:offset+12])[0]
            y2 = struct.unpack("<i", d[offset+12:offset+16])[0]
            
            if x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1:
                self.rectangles.append((-x1, -y1, x2, y2))
            offset += 16
        
        if hoop_code & 1 == 0:
            # The 4 byte words from 68 to 74 should all be -1.
            pass
        
        # The colour table always seems to start at offset 0x74.
        self.colours = []
        self.thread_types = []
        
        colour_offset = 0x74
        thread_type_offset = 0x74 + (4 * self.threads)
        for i in range(self.threads):
        
            self.colours.append(struct.unpack("<i", d[colour_offset:colour_offset+4])[0])
            self.thread_types.append(struct.unpack("<i", d[thread_type_offset:thread_type_offset+4])[0])
            colour_offset += 4
            thread_type_offset += 4
        
        self.read_threads(data)
    
    def save(self, path):
    
        self.threads = len(self.coordinates)
        thread_data = self.write_threads()
        start = 0x74 + (8 * self.threads)
        
        self._data = ""
        self._data += struct.pack("<I", start)  # data offset
        self._data += struct.pack("<I", 1)      # date-time flag
        if self.date_time:
            self._data += time.strftime("%Y%m%d%H%M%S", self.date_time)
        else:
            self._data += time.strftime("%Y%m%d%H%M%S", time.localtime())
        self._data += "\x00\x00"
        
        self._data += struct.pack("<I", self.threads)
        self._data += struct.pack("<I", len(thread_data)/2)
        
        if self.hoop_name == "A":
            self._data += struct.pack("<I", 0)
        elif self.hoop_name == "C":
            self._data += struct.pack("<I", 1)
        elif self.hoop_name == "B":
            self._data += struct.pack("<I", 2)
        elif self.hoop_name == "F":
            self._data += struct.pack("<I", 3)
        elif self.hoop_name == "D":
            self._data += struct.pack("<I", 4)
        else:
            self._data += struct.pack("<I", 0)
        
        if not self.rectangles:
        
            # Add a bounding rectangle to the output if no rectangles are
            # specified.
            self.rectangles.append(self.bounding_rect())
        
        for x1, y1, x2, y2 in self.rectangles:
        
            if len(self._data) < 0x74:
            
                self._data += struct.pack("<i", -x1)
                self._data += struct.pack("<i", -y1)
                self._data += struct.pack("<i", x2)
                self._data += struct.pack("<i", y2)
        
        # Fill the gap between the end of the rectangle list and the colour
        # table.
        while len(self._data) < 0x74:
            self._data += struct.pack("<i", -1)
        
        for i in range(self.threads):
            self._data += struct.pack("<i", self.colours[i])
        
        for i in range(self.threads):
            self._data += struct.pack("<i", self.thread_types[i])
        
        self._data += thread_data
        
        try:
            open(path, "w").write(self._data)
            return True
        except IOError:
            return False
    
    def set_colour(self, index, code):
    
        self.colours[index] = code
    
    def read_threads(self, data):
    
        self.coordinates = []
        x, y = 0, 0
        
        coordinates = []
        first = True
        i = 0
        
        while i < len(data):
        
            if data[i:i+2] == "\x80\x01":
                # Starting a new thread. Record the coordinates already read
                # and skip the next two bytes.
                if coordinates:
                    self.coordinates.append(coordinates)
                coordinates = []
                first = True
                i += 4
                continue
            elif data[i:i+2] == "\x80\x02":
                # Move command.
                i += 2
                command = "move"
                first = True
            elif data[i:i+2] == "\x80\x10":
                # End of data.
                if coordinates:
                    self.coordinates.append(coordinates)
                break
            else:
                command = "stitch"
            
            x += struct.unpack("<b", data[i])[0]
            y += struct.unpack("<b", data[i+1])[0]
            
            if command == "move":
                coordinates.append((command, x, y))
            elif first:
                coordinates.append(("move", x, y))
                first = False
            else:
                coordinates.append((command, x, y))
            
            i += 2
    
    def colour_for_thread(self, index):
    
        try:
            identifier = self.colours[index]
            colour = jef_colours.colour(identifier)
        except KeyError:
            colour = (0, 0, 0)
            sys.stderr.write("Thread %i: Failed to find colour 0x%02x (%i).\n" % (index, identifier, identifier))
        
        return colour
    
    def write_threads(self):
    
        thread_data = ""
        
        cx, cy = 0, 0
        first = True
        
        for coordinates in self.coordinates:
        
            if first:
                first = False
            else:
                thread_data += "\x80\x01"
                thread_data += "\x00\x00"
            
            for command, x, y in coordinates:
            
                if command == "move":
                    thread_data += "\x80\x02"
                
                thread_data += struct.pack("<b", x - cx)
                thread_data += struct.pack("<b", y - cy)
                
                cx = x
                cy = y
        
        thread_data += "\x80\x10"
        return thread_data
    
    def bounding_rect(self):
    
        xmin, xmax, ymin, ymax = [], [], [], []
        for coordinates in self.coordinates:
            x = map(lambda (command, x, y): x, coordinates)
            y = map(lambda (command, x, y): y, coordinates)
            xmin.append(min(x))
            xmax.append(max(x))
            ymin.append(min(y))
            ymax.append(max(y))
        
        return (min(xmin), min(ymin), max(xmax), max(ymax))

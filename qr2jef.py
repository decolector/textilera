#/usr/bin/python

from datetime import datetime
import qrcode
import jef
from Colours import jef_colours

#make the qr and get its matrix

class Qr2jef():

    def __init__(self,  queue_dir, backup_dir, max_stitch_length=127.0, unit_width=100, unit_height=100, step=10):
        self.qr = qrcode.QRCode()

        self.pattern = jef.Pattern()
        self.pattern.threads = 1
        self.max_stitch_length = max_stitch_length
        self.unit_width = unit_width
        self.unit_height = unit_height
        self.step = step
        self.queue_dir = queue_dir
        self.backup_dir = backup_dir

    def generate(self, text):
        self.pattern.coordinates = []
        self.qr.clear()
        self.qr.add_data(text)
        self.qr.make()
        self.matrix = self.qr.get_matrix()
        #set up color data
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

        #get color code for black
        internal_code = colours.get("#000000", 2)
        coords = []
        y = 0

        """
        for row in matrix:
        	x = 0
        	for col in row:
        		#print "x: ", x, " y: ", y
        		if col:
        			coords.append(("stitch", int(x),int(-y)))
        			coords.append(("stitch", int(x+unit_width), int(-y)))
        			coords.append(("stitch", int(x+unit_width), int(-(y+unit_height))))
        			coords.append(("stitch", int(x), int(-(y+unit_height))))
        			coords.append(("stitch", int(x),int(-y)))
        		x += unit_width

        	y += unit_height
        """
        for row in self.matrix:
        	x = 0
        	for col in row:
        		#print "x: ", x, " y: ", y
        		if col:
        			for i in range(0, self.unit_height, self.step):
        				y1 = y+i
        				coords.append(("stitch", int(x), int(-y1)))
        				coords.append(("stitch", int(x+self.unit_width), int(-y1)))

        		x += self.unit_width
        	y += self.unit_height

        self.pattern.coordinates.append(coords)

        x1, y1, x2, y2 = self.pattern.bounding_rect()
        dx = -(x2 - x1)/2 - x1
        dy = -(y2 - y1)/2 - y1

        cx, cy = 0, 0

        for coordinates in self.pattern.coordinates:

            i = 0
            while i < len(coordinates):
            
                command, x, y = coordinates[i]
                x = int(x + dx)
                y = int(y + dy)
                
                # If one or both dimensions are greater than the maximum stitch
                # length then split the line into pieces.
                d = max(abs(x - cx), abs(y - cy))
                n = (d / self.max_stitch_length)
                
                if n > 1:
                
                    xs = max(-self.max_stitch_length, min(float(x - cx)/n, self.max_stitch_length))
                    ys = max(-self.max_stitch_length, min(float(y - cy)/n, self.max_stitch_length))
                    
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

        self.pattern.colours.append(internal_code)
        self.pattern.thread_types.append(13)
        dt = datetime.now().strftime("%H_%M_%S%p-%d_%B_%Y")
        jef_filename = "%sqrcode_%s.jef" %self.queue_dir, dt
        backup_filename = "%sqrcode_%s.jef" %self.backup_dir, dt 
        img_filename = "%sqrcode_%s.png" %self.backup_dir, dt
        print filename
        im = qr.make_image()
        im.save(img_filename, "PNG")
        self.pattern.save(filename)
        self.pattern.save(backup_filename)


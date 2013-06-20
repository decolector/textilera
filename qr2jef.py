#/usr/bin/python

import qrcode
import jef
from Colours import jef_colours

#make the qr and get its matrix
qr = qrcode.QRCode()
qr.add_data("texto")
qr.make()
matrix = qr.get_matrix()


pattern = jef.Pattern()
pattern.threads = 1

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
unit_width = 100
unit_height = 100
y = 0

for row in matrix:
	x = 0
	for col in row:
		if col:
			pattern.coordinates.append([("stitch", x,y), 
				("stitch", x+unit_width, -y),
				("stitch", x+unit_width, -(y+unit_height)),
				("stitch", x, -(y+unit_height)),
				("stitch", x,-y)
				])
		x = x+unit_width
	y = y + unit_height

#pattern.coordinates.append(coords)
pattern.colours.append(internal_code)
pattern.thread_types.append(13)

pattern.save("auto_qr.jef")


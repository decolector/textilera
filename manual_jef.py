#/usr/bin/python

#creates a square of 100x100 and saves it to a jef file

import jef
from Colours import jef_colours


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

#coordinates
coords = [("move", 30, -120),("stitch", 30,-80),("stitch", 80,0), ("stitch",180,0), ("stitch", 120, -120),("stitch", 0,-120), ("stitch", 0,0)]


#write data to pattern
pattern.coordinates.append(coords)
pattern.colours.append(internal_code)
pattern.thread_types.append(13)

#save file
pattern.save("manual_rect.jef")

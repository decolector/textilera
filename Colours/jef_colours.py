#!/usr/bin/env python

import csv, os

import all_colours
import janome_colours
import robison_rayon_colours
import robison_polyester_colours
import sulky_rayon_colours
import measured_colours


def read_colours():

    f = open(os.path.join(os.path.split(__file__)[0], "colours.csv"))
    r = csv.reader(f)
    colour_groups = r.next()
    
    known_colours = all_colours.groups
    known_colours.update(janome_colours.groups)
    known_colours.update(robison_rayon_colours.groups)
    known_colours.update(robison_polyester_colours.groups)
    known_colours.update(sulky_rayon_colours.groups)
    
    default_colours = {}
    colour_mappings = {}
    
    # Examine the rows in the CSV file mapping internal colour codes to other
    # colour codes, looking up each code in the dictionaries mapping colour codes
    # to known colours.
    
    for row in r:
    
        internal_code = int(row[0])
        
        for group, other_code in zip(colour_groups[1:], row[1:]):
        
            if other_code and known_colours.has_key(group):
            
                colours_dict = known_colours[group]
                other_code = int(other_code)
                
                if not colours_dict.has_key(other_code):
                    continue
                
                colour_mappings.setdefault(internal_code, {})[group] = other_code
                
                if default_colours.has_key(internal_code):
                    continue
                
                try:
                    default_colours[internal_code] = colours_dict[other_code]
                except KeyError:
                    pass
    
    f.close()
    return colour_groups[1:], known_colours, default_colours, colour_mappings


def colour(identifier):

    try:
        name, rgb = default_colours[identifier]
    except KeyError:
        name, rgb = measured_colours.colours[identifier]
    
    return int(rgb[1:3], 16), int(rgb[3:5], 16), int(rgb[5:7], 16)


colour_groups, known_colours, default_colours, colour_mappings = read_colours()

# Polygon fill code adapted from:
# http://alienryderflex.com/polygon_fill/
# optimized to use a list of dictionaries
# to store polygon coordinates and 
# built in list sorting

import svgwrite

poly = [{'x': 20.0, 'y':180.0},
        {'x': 80.0, 'y':100.0},
        {'x': 180.0, 'y': 50.0},
        {'x': 270.0, 'y': 100.0},
        {'x': 370.0, 'y': 250.0},
        {'x': 250.0, 'y':350.0},
        {'x': 230.0, 'y': 240.0},
        {'x': 200.0, 'y': 370.0},
        {'x': 180.0, 'y': 250.0},
        {'x': 80.0, 'y': 200.0},
        {'x': 20.0, 'y': 180.0}]

d = svgwrite.Drawing(filename = "polyFillOpti.svg", debug=True)
p = svgwrite.path.Path(style='fill:none;stroke:#000000;stroke-width:1px')
p.push('M')

#build a list of nodes
for a in range(500): #iterate over height of the coordinate system
    nodeX = []
    for coord in range(len(poly)-1):
        next_coord = coord + 1
        if poly[coord]['y'] < float(a) and poly[next_coord]['y'] >= float(a) or poly[next_coord]['y'] < float(a) and poly[coord]['y'] >= float(a):
            nodeX.append(int(poly[coord]['x'] + (a - poly[coord]['y']) / (poly[next_coord]['y'] - poly[coord]['y']) * (poly[next_coord]['x'] - poly[coord]['x'])))

    #sort the nodes
    nodeX.sort()
    
    # loop to draw the lines
    for x in range(0, len(nodeX),2):
        p.push(nodeX[x],a, nodeX[x+1],a)

p.push('Z')
d.add(p)
d.save()

# Polygon fill code adapted from:
# http://alienryderflex.com/polygon_fill/
# this code is pretty much ported as is found
# see polyFillOptimized for a shorter version of it

import svgwrite

d = svgwrite.Drawing(filename = "polyFill.svg", debug=True)
p = svgwrite.path.Path(style='fill:none;stroke:#000000;stroke-width:1px')
p.push('M')
polyX = [20.0, 80.0, 180.0, 270.0, 370.0, 250.0, 230.0, 200.0, 180.0, 80.0, 20.0];
polyY = [180.0, 100.0, 50.0, 100.0, 250.0, 350.0, 240.0, 370.0, 250.0, 200.0, 180.0]
nodes = 0

polyCorners = len(polyX)

#build a list of nodes
for a in range(500): #iterate over height of the coordinate system
    nodeX = []
    j = polyCorners -1;
    for i in range(polyCorners):
        if polyY[i] < float(a) and polyY[j] >= float(a) or polyY[j] < float(a) and polyY[i] >= float(a):
            nodeX.append(int(polyX[i] + (a - polyY[i]) / (polyY[j] - polyY[i]) * (polyX[j] - polyX[i])))
        
        j = i

    #sort the nodes
    i = 0
    while i < nodes - 1:
        if nodeX[i] > nodeX[i+1]:
            swap = nodeX[i]
            nodeX[i] = nodeX[i+1]
            if i > 0:
                i = i - 1

            else:
                i = i + 1
    print "len nodeX: ", len(nodeX)
    for x in range(0, len(nodeX),2):
        #draw the line
        p.push(nodeX[x],a, nodeX[x+1],a)

p.push('Z')
d.add(p)
d.save()

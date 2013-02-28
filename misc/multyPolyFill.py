"""
Hatchline fill for multiple polygons
Based on:

http://alienryderflex.com/polygon_hatchline_fill/

poly 1 (clockwise)

X    Y
50, 50
100, 50
100, 150
150, 150
150, 250
50, 250

poly 2 (clockwise)

200, 100
300, 100
300, 150
250, 150
250, 200
200, 200

"""
import svgwrite

d = svgwrite.Drawing(filename = "multiPolyFill.svg", debug= True)
p = svgwrite.path.Path(style = "fill:none;stroke:#000000;stroke-width:1px")
p.push('M')

nodeX = []
nodeY = []

poly_1 = [(50, 50),
        (100, 50),
        (100, 150),
        (150, 150),
        (150, 250),
        (50, 250)]

poly_2 = [(200, 100),
        (300, 100),
        (300, 150),
        (250, 150),
        (250, 200),
        (200, 200)]


polygons = [poly_1, poly_2]

# loop over the height of canvas to build a list of nodes
for a in range(500):
    for poly in polygons:
        #print 'poly length: ', len(poly)
        for coord in range(len(poly)-1):
            _next = coord + 1 #index of the next coordinate
            if poly[coord][1] < float(a) and poly[_next][1] >= float(a) or poly[_next][1] < float(a) and poly[coord][1] >= float(a):
                nodeX.append(int(poly[coord][0] + (a - poly[coord][1]) / (poly[_next][1] - poly[coord][1]) * (poly[_next][0] - poly[coord][0])))
                nodeY.append(a)
    
        
#sort the nodes
nodeX.sort()
#print len(nodeX)

for x in range(0, len(nodeX), 2):
    p.push(nodeX[x], nodeY[x], nodeX[x+1], nodeY[x+1])

p.push('Z')
d.add(p)
d.save()



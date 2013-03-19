"""
Hatchline fill for multiple polygons
Based on:

http://alienryderflex.com/polygon_hatchline_fill/

"""
import svgwrite
import qrcode
import numpy
import potrace


#fill polygons with parallel lines
#and saves to svg

def fill(polygons, height):
    d = svgwrite.Drawing(filename = "qr_filled.svg", debug= True)
    p = svgwrite.path.Path(style = "fill:none;stroke:#000000;stroke-width:1px")
    p.push('M', 0.0, 0.0)

    
    for poly in polygons:
        for a in range(0, height, 1):
            nodeX = []
            #print 'poly length: ', len(poly)
            for coord in range(len(poly)-1):
                _next = coord + 1 #index of the next coordinate
                if poly[coord][1] < float(a) and poly[_next][1] >= float(a) or poly[_next][1] < float(a) and poly[coord][1] >= float(a):
                    nodeX.append(int(poly[coord][0] + (a - poly[coord][1]) / (poly[_next][1] - poly[coord][1]) * (poly[_next][0] - poly[coord][0])))
                
            #sort the nodes
            nodeX.sort()
            #nodeY.sort();
            
            if(len(nodeX) > 1):
                for x in range(0, len(nodeX), 2):
                    p.push('M', nodeX[x], float(a))
                    p.push('L', nodeX[x+1], float(a))

    d.add(p)
    d.save()


#contour polygons and save to svg
def contour(polygons):
    d = svgwrite.Drawing(filename = "qr_filled.svg", debug= True)
    p = svgwrite.path.Path(style = "fill:none;stroke:#000000;stroke-width:1px")
    p.push('M', 0.0, 0.0)
   
    for poly in polygons:
        p.push('M', poly[0][0], poly[0][1])
        for point in poly:
            p.push('L', point[0], point[1])

    d.add(p)
    d.save()


qr = qrcode.make('hola')
temp = qr._img
height = temp.size[1]
temp.convert('L')
bit = potrace.Bitmap(numpy.asarray(temp)) 
traced = bit.trace(turdsize = 5, 
        turnpolicy = potrace.TURNPOLICY_RANDOM, 
        alphamax = 0.0, 
        opticurve = 1, 
        opttolerance = 0.1)
polygons = []

for curve in traced.curves:
    print "children: ", len(curve.children)
    vertex = []
    for segment in curve:
        
        #we just need the corners
        """
        if segment.is_corner:
        
            vertex.append(segment.end_point)
            print(segment.end_point)
        """
        #or we need everything
        vertex.append(segment.end_point)

    if len(vertex) > 0:
        #append copy the first point at the end
        vertex.append(vertex[0])
        print vertex[0], " and ", vertex[-1]

    polygons.append(vertex)

#contour or fill
#fill(polygons, height)
contour(polygons)




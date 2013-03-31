import svgwrite
import qrcode
import numpy
import potrace

qr = qrcode.make('hola')
temp = qr._img
height = temp.size[1]
bmp = temp.convert('L')
#temp.show()
#bmp.save("qr.bmp")
bit = potrace.Bitmap(numpy.asarray(bmp))
#traced = bit.trace()

traced = bit.trace(turdsize = 5, 
        turnpolicy = potrace.TURNPOLICY_MAJORITY, 
        alphamax = 1.0, 
        opticurve = 0, 
        opttolerance = 0.2)

d = svgwrite.Drawing(filename = "qr_tracer.svg", debug= True)
p = svgwrite.path.Path(style = "fill:none;stroke:#000000;stroke-width:1px")
p.push('M', 0.0, 0.0)


polygons = []

for curve in traced:
    p.push('M',curve.start_point[0], curve.start_point[1])
    p.push('L')
    for segment in curve:
        #if segment.is_corner:
            #print segment.end_point
        p.push(segment.end_point[0], segment.end_point[1])
    if curve.children:
        print "this has child"
        for child in curve.children:
            p.push('M', child.start_point[0], child.start_point[1])
            p.push('L')
            for seg in child:
                p.push(seg.end_point[0], seg.end_point[1])

d.add(p)
d.save()


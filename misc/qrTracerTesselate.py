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
        turnpolicy = potrace.TURNPOLICY_MINORITY, 
        alphamax = 0.0, 
        opticurve = 0, 
        opttolerance = 0.2)

d = svgwrite.Drawing(filename = "qr_tracer_tess.svg", debug= True)
p = svgwrite.path.Path(style = "fill:none;stroke:#000000;stroke-width:1px")
p.push('M', 0.0, 0.0)


polygons = []

for curve in traced:
    tess = curve.tesselate(potrace.Curve.adaptive)
    print tess
    
    p.push('M',curve.start_point[0], curve.start_point[1])
    p.push('L')
    for point in tess:
        p.push(point[0], point[1])


d.add(p)
d.save()

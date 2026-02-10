import bpy

# Crear curva
curve_data = bpy.data.curves.new('BezierCurve', type='CURVE')
curve_data.dimensions = '3D'

spline = curve_data.splines.new(type='BEZIER')
spline.bezier_points.add(2)

# Definir puntos de control
points = spline.bezier_points
points[0].co = (0, 0, 0)
points[1].co = (2, 2, 0)
points[2].co = (4, 0, 0)

# Ajustar handles
for p in points:
    p.handle_left_type = 'AUTO'
    p.handle_right_type = 'AUTO'

# Crear objeto
curve_obj = bpy.data.objects.new('BezierObj', curve_data)
bpy.context.collection.objects.link(curve_obj)
import bpy
import mathutils
import numpy as np

# =========================
# CONFIGURACIÓN
# =========================

kpuntuak = np.array([
    [2.0, 1.0, 0.0],
    [2.5, 2.5, 0.5],
    [0.5, 2.0, 1.0],
    [0.0, 1.0, 1.5],
    [1.0, 0.0, 2.5]
])

control_points = [mathutils.Vector(p) for p in kpuntuak]

steps = 60          # Más pasos para curva más suave
show_levels = True  # Mostrar niveles intermedios

# =========================
# LIMPIAR ESCENA
# =========================

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# =========================
# FUNCIONES
# =========================

def create_curve(name, points, color=(1,1,1,1), bevel=0.02):
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 4

    spline = curve_data.splines.new('POLY')
    spline.points.add(len(points) - 1)

    for i, p in enumerate(points):
        spline.points[i].co = (*p, 1)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)

    # Color visible en Solid y Material Preview
    obj.color = color

    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.4
    obj.data.materials.append(mat)

    return obj




def lerp(p0, p1, t):
    return (1 - t) * p0 + t * p1


def de_casteljau(points, t):
    levels = [points]
    while len(points) > 1:
        points = [lerp(points[i], points[i+1], t)
                  for i in range(len(points)-1)]
        levels.append(points)
    return levels

# =========================
# PUNTOS DE CONTROL
# =========================

for i, p in enumerate(control_points):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=p)
    bpy.context.object.name = f"CP_{i}"

create_curve("Control_Polygon", control_points, (0.7, 0.7, 0.7, 1))

# =========================
# CURVA DE BÉZIER FINAL
# =========================

bezier_points = []

for i in range(steps + 1):
    t = i / steps
    levels = de_casteljau(control_points, t)
    bezier_points.append(levels[-1][0])

create_curve("Bezier_Curve", bezier_points, (1, 0, 0, 1))

# =========================
# NIVELES DE CASTELJAU
# =========================

if show_levels:
    t_demo = 0.5
    levels = de_casteljau(control_points, t_demo)

    colors = [
        (0, 0, 1, 1),
        (0, 1, 0, 1),
        (1, 0.5, 0, 1),
        (0.6, 0, 0.6, 1)
    ]

    for level, pts in enumerate(levels[1:-1]):
        create_curve(
            f"Level_{level+1}",
            pts,
            colors[level % len(colors)]
        )

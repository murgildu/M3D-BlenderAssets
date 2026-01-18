"""
Lab 05.5.2–05.5.3 — Bézier cúbica por fórmula vs Blender + tangentes en extremos
=================================================================================

Relación Bernstein ↔ Bézier
---------------------------
Una Bézier cúbica puede definirse directamente usando Bernstein:

    P(u) = P0 B0(u) + P1 B1(u) + P2 B2(u) + P3 B3(u),   u ∈ [0,1]

donde B0..B3 son los Bernstein cúbicos.

Equivalencia con Blender (segmento Bézier)
------------------------------------------
Un segmento Bézier cúbico estándar se representa en Blender con 2 "Bezier Points":
- Punto A: co = P0, handle_right = P1
- Punto B: co = P3, handle_left  = P2
(Asumiendo handles en modo FREE para fijar posiciones exactas.)

Tangentes en extremos
---------------------
Derivada de la Bézier cúbica:
- P'(0) = 3 (P1 - P0)
- P'(1) = 3 (P3 - P2)

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crean:
   - BezierFormula (mesh polilínea) -> muestreo de la fórmula
   - BezierBlender (Curve Bézier)  -> spline nativa de Blender
   - ControlPolygon (mesh)         -> polígono P0-P1-P2-P3
   - Flechas Tangent0 y Tangent1   -> tangentes en extremos
3) Modificar P0..P3 en el script y re-ejecutar para observar cambios.
"""

import bpy
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab05_5_2_BezierCompare"

# Muestreo de la curva por fórmula
N_SAMPLES = 160

# Puntos de control (editables)
P0 = Vector((0.0, 0.0, 0.0))
P1 = Vector((1.5, 2.0, 0.0))
P2 = Vector((3.0, -2.0, 0.0))
P3 = Vector((4.5, 0.0, 0.0))

# Longitud visual de flechas tangentes (escala)
TANGENT_ARROW_LEN = 1.4

# Flecha (actualizable / simple)
ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
UNIT_ARROW_HEAD_FRAC = 0.25

KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
    "LAB02_2_3_LAMBERT_DRAW_HANDLER",
    "LAB02_2_4_THRESHOLD_DRAW_HANDLER",
    "LAB03_3_4_PARAMETRIC_HELIX_DRAW_HANDLER",
    "LAB04_TANGENT_DRAW_HANDLER",
    "LAB05_5_1_BERNSTEIN_DRAW_HANDLER",
    "LAB05_5_2_BEZIER_DRAW_HANDLER",
]

# -----------------------------
# Limpieza HUD (por compatibilidad)
# -----------------------------
def remove_handler_by_key(key: str) -> None:
    ns = bpy.app.driver_namespace
    handler = ns.get(key)
    if handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")
        except Exception:
            pass
        ns.pop(key, None)

def remove_all_known_lab_handlers() -> None:
    for k in KNOWN_HANDLER_KEYS:
        remove_handler_by_key(k)

# -----------------------------
# Limpieza escena
# -----------------------------
def wipe_scene() -> None:
    try:
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    master = bpy.context.scene.collection
    for child in list(master.children):
        master.children.unlink(child)
        try:
            bpy.data.collections.remove(child)
        except Exception:
            pass

    for datablock in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.objects):
        for block in list(datablock):
            if block.users == 0:
                try:
                    datablock.remove(block)
                except Exception:
                    pass

# -----------------------------
# Colecciones
# -----------------------------
def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def move_object_to_collection_only(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)

# -----------------------------
# Bernstein cúbico
# -----------------------------
def B0(u: float) -> float:
    return (1.0 - u) ** 3

def B1(u: float) -> float:
    return 3.0 * u * (1.0 - u) ** 2

def B2(u: float) -> float:
    return 3.0 * (u ** 2) * (1.0 - u)

def B3(u: float) -> float:
    return u ** 3

def bezier_point(u: float) -> Vector:
    return (P0 * B0(u) + P1 * B1(u) + P2 * B2(u) + P3 * B3(u))

# -----------------------------
# Mesh polilínea
# -----------------------------
def build_polyline_mesh(points: list[Vector], name: str, closed: bool = False) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    verts = [(p.x, p.y, p.z) for p in points]
    edges = [(i, i + 1) for i in range(len(points) - 1)]
    if closed and len(points) > 2:
        edges.append((len(points) - 1, 0))
    faces = []
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    return obj

def sample_bezier_formula(n: int) -> list[Vector]:
    pts = []
    for i in range(n):
        u = i / (n - 1)
        pts.append(bezier_point(u))
    return pts

# -----------------------------
# Curve Bézier nativa (2 puntos)
# -----------------------------
def create_blender_bezier(name: str = "BezierBlender") -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=name + "_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 24

    spline = curve_data.splines.new(type="BEZIER")
    spline.bezier_points.add(1)  # 2 puntos

    bp0 = spline.bezier_points[0]
    bp1 = spline.bezier_points[1]

    # Importante: modo FREE para fijar handles exactamente
    bp0.handle_left_type = "FREE"
    bp0.handle_right_type = "FREE"
    bp1.handle_left_type = "FREE"
    bp1.handle_right_type = "FREE"

    bp0.co = P0
    bp1.co = P3
    bp0.handle_right = P1
    bp1.handle_left = P2

    obj = bpy.data.objects.new(name, curve_data)
    return obj

# -----------------------------
# Flechas de tangente
# -----------------------------
def create_cylinder(name: str, radius: float, depth: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_cone(name: str, radius: float, depth: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0.0, depth=depth, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def orient_object_from_z_axis(obj: bpy.types.Object, direction: Vector) -> None:
    if direction.length < 1e-12:
        return
    d = direction.normalized()
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = z_axis.rotation_difference(d)

def create_unit_arrow(col, base_name: str, start: Vector) -> dict:
    root = bpy.data.objects.new(base_name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.location = start
    col.objects.link(root)

    shaft = create_cylinder(f"{base_name}_shaft", ARROW_SHAFT_RADIUS, 1.0)
    head = create_cone(f"{base_name}_head", ARROW_HEAD_RADIUS, 1.0)

    move_object_to_collection_only(shaft, col)
    move_object_to_collection_only(head, col)

    shaft.parent = root
    head.parent = root
    return {"root": root, "shaft": shaft, "head": head}

def update_arrow(arrow: dict, start: Vector, vec: Vector, desired_length: float) -> None:
    root, shaft, head = arrow["root"], arrow["shaft"], arrow["head"]
    root.location = start

    if vec.length < 1e-12:
        shaft.scale = Vector((1.0, 1.0, 0.0001))
        head.scale = Vector((1.0, 1.0, 0.0001))
        shaft.location = Vector((0.0, 0.0, 0.0))
        head.location = Vector((0.0, 0.0, 0.0))
        return

    orient_object_from_z_axis(root, vec)

    L = max(0.001, float(desired_length))
    head_len = max(0.05, min(L * UNIT_ARROW_HEAD_FRAC, 0.4))
    shaft_len = max(0.001, L - head_len)

    shaft.scale = Vector((1.0, 1.0, shaft_len))
    head.scale = Vector((1.0, 1.0, head_len))
    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))

# -----------------------------
# Tangentes teóricas
# -----------------------------
def tangent_at_0() -> Vector:
    return 3.0 * (P1 - P0)

def tangent_at_1() -> Vector:
    return 3.0 * (P3 - P2)

# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()
    col = ensure_collection(LAB_COLLECTION_NAME)

    # 1) Polígono de control P0-P1-P2-P3
    ctrl_poly = build_polyline_mesh([P0, P1, P2, P3], "ControlPolygon", closed=False)
    bpy.context.scene.collection.objects.link(ctrl_poly)
    move_object_to_collection_only(ctrl_poly, col)

    # 2) Curva por fórmula (mesh polilínea)
    pts = sample_bezier_formula(N_SAMPLES)
    formula_obj = build_polyline_mesh(pts, "BezierFormula", closed=False)
    bpy.context.scene.collection.objects.link(formula_obj)
    move_object_to_collection_only(formula_obj, col)

    # 3) Curva Bézier nativa (Blender)
    blender_obj = create_blender_bezier("BezierBlender")
    bpy.context.scene.collection.objects.link(blender_obj)
    move_object_to_collection_only(blender_obj, col)

    # 4) Flechas de tangente
    t0 = tangent_at_0()
    t1 = tangent_at_1()

    arrow0 = create_unit_arrow(col, "Tangent0", P0)
    arrow1 = create_unit_arrow(col, "Tangent1", P3)
    update_arrow(arrow0, P0, t0, TANGENT_ARROW_LEN)
    update_arrow(arrow1, P3, t1, TANGENT_ARROW_LEN)

    # Selección
    bpy.ops.object.select_all(action="DESELECT")
    blender_obj.select_set(True)
    bpy.context.view_layer.objects.active = blender_obj

    # Reporte numérico (útil en consola)
    print("=== Lab 05.5.2–05.5.3 — Bézier por fórmula vs Blender ===")
    print(f"P0={tuple(P0)}  P1={tuple(P1)}  P2={tuple(P2)}  P3={tuple(P3)}")
    print(f"P'(0) = 3(P1-P0) = {tuple(t0)}")
    print(f"P'(1) = 3(P3-P2) = {tuple(t1)}")
    print("Objetos creados: ControlPolygon, BezierFormula (mesh), BezierBlender (curve), Tangent0, Tangent1")

if __name__ == "__main__":
    main()


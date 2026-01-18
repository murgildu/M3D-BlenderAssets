"""
Lab 06.6.3 — Aproximar continuidad C1 ajustando handles en Blender
==================================================================

Objetivo
--------
Conseguir continuidad C1 en el empalme de dos segmentos Bézier:
- Tangentes izquierda y derecha en el punto de unión J deben ser:
  1) colineales (como en G1)
  2) de igual magnitud (condición adicional de C1)

Criterio práctico
-----------------
- G1: angle(T_left, T_right) ~ 0
- C1: además |T_left| ~ |T_right|

En términos de handles en el punto central J:
- Handle izquierdo y derecho deben estar en la misma recta
- y a la misma distancia del punto J (simetría)

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Seleccionar "SplineC1Task" y entrar en Edit Mode.
3) En el punto central J:
   - Alinear handles (G1)
   - Igualar sus longitudes (C1 aproximado)
4) Ejecutar el checker para confirmar.

Mini-diagrama ASCII
-------------------
G1 (dirección):        C1 (dirección + magnitud):
   <---*---->             <----*---->
(longitudes distintas)    (longitudes iguales)
"""

import bpy
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab06_6_3_C1Task"

# -----------------------------
# Limpieza escena (estándar)
# -----------------------------
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
    "LAB02_2_3_LAMBERT_DRAW_HANDLER",
    "LAB02_2_4_THRESHOLD_DRAW_HANDLER",
    "LAB05_5_1_BERNSTEIN_DRAW_HANDLER",
    "LAB06_6_1_CONTINUITY_DRAW_HANDLER",
]

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
# Crear spline para tarea C1
# -----------------------------
def create_bezier_task() -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name="SplineC1Task_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 24

    spline = curve_data.splines.new(type="BEZIER")
    spline.bezier_points.add(2)  # 3 puntos

    P0 = Vector((0.0, 0.0, 0.0))
    J  = Vector((2.0, 0.0, 0.0))
    P3 = Vector((4.0, 1.5, 0.0))

    bp0 = spline.bezier_points[0]
    bp1 = spline.bezier_points[1]  # join
    bp2 = spline.bezier_points[2]

    for bp in (bp0, bp1, bp2):
        bp.handle_left_type = "FREE"
        bp.handle_right_type = "FREE"

    bp0.co = P0
    bp1.co = J
    bp2.co = P3

    # Inicial: C0 clara (esquina) y además longitudes diferentes
    bp0.handle_right = P0 + Vector((0.8, 1.2, 0.0))
    bp1.handle_left  = J  + Vector((-1.2, -1.2, 0.0))  # más largo
    bp1.handle_right = J  + Vector((0.6, 0.0, 0.0))    # más corto
    bp2.handle_left  = P3 + Vector((-0.8, 0.0, 0.0))

    obj = bpy.data.objects.new("SplineC1Task", curve_data)
    return obj


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    obj = create_bezier_task()
    bpy.context.scene.collection.objects.link(obj)
    move_object_to_collection_only(obj, col)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print("=== Lab 06.6.3 — Aproximar C1 editando handles ===")
    print("La escena previa ha sido eliminada.")
    print("Objeto creado: SplineC1Task (Curve Bézier con 2 segmentos).")
    print("Acción: Edit Mode -> en el punto central, alinear handles y hacerlos simétricos (misma longitud).")
    print("Luego ejecutar el checker.")

if __name__ == "__main__":
    main()


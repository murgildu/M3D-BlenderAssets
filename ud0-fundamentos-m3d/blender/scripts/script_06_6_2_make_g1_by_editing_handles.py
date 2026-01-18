"""
Lab 06.6.2 — Lograr continuidad G1 ajustando handles en Blender
===============================================================

Objetivo
--------
Conseguir continuidad geométrica G1 en el empalme de dos segmentos Bézier:
- En el punto de unión J, las tangentes izquierda y derecha deben tener la MISMA dirección
  (pueden tener distinta magnitud).

Formalmente:
- Sea T_left la tangente al llegar a J desde el segmento anterior.
- Sea T_right la tangente al salir de J hacia el siguiente segmento.
G1 equivale a que T_left y T_right sean colineales (ángulo ~ 0 grados).

Montaje
-------
Se crean 3 puntos Bézier: P0, J, P3 (dos segmentos: P0->J y J->P3).
La configuración inicial está en C0 (hay una esquina visible).

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Seleccionar "SplineG1Task" y entrar en Edit Mode.
3) En el punto J (el central):
   - Ajustar los handles para que estén ALINEADOS (misma dirección).
   - No es necesario que tengan la misma longitud.
4) Ejecutar el checker para confirmar que el ángulo entre tangentes es pequeño.

Sugerencia en Blender
---------------------
- En Edit Mode, selecciona el punto central J.
- Alinea los handles (izquierdo y derecho) en la misma recta.
- Se busca una unión "suave a ojo" (sin pico).

Mini-diagrama ASCII
-------------------
C0 (esquina):       G1 (suave):
   \                  \
    \                  \
     *----              *-----
"""

import bpy
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab06_6_2_G1Task"

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
# Crear spline para tarea G1
# -----------------------------
def create_bezier_task() -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name="SplineG1Task_Data", type="CURVE")
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

    # Configuración inicial C0 (pico):
    bp0.handle_right = P0 + Vector((0.8, 1.2, 0.0))
    bp1.handle_left  = J  + Vector((-0.8, -1.2, 0.0))  # NO alineado con el derecho
    bp1.handle_right = J  + Vector((0.8, 0.0, 0.0))
    bp2.handle_left  = P3 + Vector((-0.8, 0.0, 0.0))

    obj = bpy.data.objects.new("SplineG1Task", curve_data)
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

    # Selección para comodidad
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print("=== Lab 06.6.2 — Lograr G1 editando handles ===")
    print("La escena previa ha sido eliminada.")
    print("Objeto creado: SplineG1Task (Curve Bézier con 2 segmentos).")
    print("Acción: Edit Mode -> alinear los handles del punto central para eliminar el pico (G1).")
    print("Luego ejecutar el checker.")

if __name__ == "__main__":
    main()


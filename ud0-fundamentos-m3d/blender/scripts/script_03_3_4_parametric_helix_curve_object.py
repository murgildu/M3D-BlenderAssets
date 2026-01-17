"""
Lab 03.3.4 — Generador de curvas paramétricas: hélice (objeto Curve)
====================================================================

Objetivo
--------
Generar una curva nativa de Blender (tipo Curve) a partir de una formulación paramétrica,
sin "dibujar" manualmente en el viewport.

Modelo paramétrico (hélice circular)
------------------------------------
Para un parámetro u en [0, 1]:

    x(u) = a cos(2π * turns * u)
    y(u) = a sin(2π * turns * u)
    z(u) = b * u

donde:
- a: radio
- turns: número de vueltas
- b: altura total (porque u va de 0 a 1)

Concepto clave
--------------
- La curva se define por muestreo: elegimos N_SAMPLES valores de u.
- Cuantas más muestras, más suave la curva (a igual settings de la curva).
- Un objeto Curve permite bevel/extrusión y resolución de forma nativa en Blender.

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crea un objeto de tipo Curve llamado "HelixCurve".
3) Recomendado (para explorar):
   - Seleccionar HelixCurve -> Object Data Properties (icono de curva verde)
   - Ajustar:
     - Resolution U
     - Bevel Depth / Bevel Resolution
     - Fill Caps
4) Modificar parámetros del script (a, b, turns, N_SAMPLES) y re-ejecutar.

Mini-diagrama ASCII
-------------------
z ^
  |        o
  |      o
  |    o
  |  o
  | o
  +-----------------> (x,y) en círculo (radio a)
"""

import bpy
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab03_3_4_ParametricHelix"

# -----------------------------
# Parámetros editables
# -----------------------------
a = 1.5          # radio
turns = 4.0      # número de vueltas
b = 3.0          # altura total (z final)
N_SAMPLES = 200  # muestras de u (más -> más suave la curva muestreada)

# Ajustes del objeto Curve (visual)
CURVE_RESOLUTION_U = 12     # resolución interna de Blender (spline resolution)
BEVEL_DEPTH = 0.03          # grosor (0 para solo línea)
BEVEL_RESOLUTION = 4
FILL_CAPS = True


def P(u: float) -> Vector:
    """Hélice circular parametrizada por u ∈ [0,1]."""
    ang = 2.0 * math.pi * turns * u
    x = a * math.cos(ang)
    y = a * math.sin(ang)
    z = b * u
    return Vector((x, y, z))


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
    # Curvas futuras (si hubiese HUD)
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
# Construcción de Curve
# -----------------------------
def sample_points(n: int) -> list[Vector]:
    if n < 2:
        raise ValueError("N_SAMPLES debe ser >= 2")
    pts = []
    for i in range(n):
        u = i / (n - 1)
        pts.append(P(u))
    return pts


def create_curve_object(points: list[Vector], name: str = "HelixCurve") -> bpy.types.Object:
    """
    Crea un objeto Curve (spline POLY) y asigna points como puntos de control.
    POLY: interpola linealmente entre puntos (la suavidad depende del muestreo).
    """
    curve_data = bpy.data.curves.new(name=name + "_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = CURVE_RESOLUTION_U

    spline = curve_data.splines.new(type="POLY")
    spline.points.add(len(points) - 1)  # ya existe 1 por defecto

    for i, p in enumerate(points):
        spline.points[i].co = (p.x, p.y, p.z, 1.0)  # w=1

    curve_data.bevel_depth = BEVEL_DEPTH
    curve_data.bevel_resolution = BEVEL_RESOLUTION
    curve_data.use_fill_caps = FILL_CAPS

    obj = bpy.data.objects.new(name, curve_data)
    return obj


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    pts = sample_points(N_SAMPLES)
    curve_obj = create_curve_object(pts, "HelixCurve")

    bpy.context.scene.collection.objects.link(curve_obj)
    move_object_to_collection_only(curve_obj, col)

    bpy.ops.object.select_all(action="DESELECT")
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj

    print("=== Lab 03.3.4 — Hélice paramétrica (Curve object) ===")
    print("La escena previa ha sido eliminada.")
    print(f"a (radio) = {a}")
    print(f"turns     = {turns}")
    print(f"b (altura)= {b}")
    print(f"N_SAMPLES = {N_SAMPLES}")
    print("Objeto creado: HelixCurve (tipo Curve).")
    print("Explorar en Blender: Object Data Properties -> Resolution/Bevel.")


if __name__ == "__main__":
    main()


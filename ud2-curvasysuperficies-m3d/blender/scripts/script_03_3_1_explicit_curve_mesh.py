"""
Lab 03.3.1 — Curva explícita y = f(x) muestreada con una malla (mesh)
=====================================================================

Objetivo
--------
Construir una curva 2D en el plano XY a partir de una función explícita:
    y = f(x)
muestreando puntos y conectándolos mediante aristas.

Concepto clave
--------------
- Formulación explícita: y depende directamente de x.
- Ventaja: evaluar f(x) es directo.
- Limitación: no todas las curvas se expresan cómodamente como y=f(x)
  (por ejemplo, circunferencias completas fallan el "test de función").

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crea un objeto mesh "ExplicitCurve" (polilínea con aristas).
3) Modificar parámetros en el script (f(x), rango, N_SAMPLES) y re-ejecutar.

Mini-diagrama ASCII
-------------------
y
^          . . . . .  (puntos muestreados)
|       .'
|    .'
| .'
+------------------------> x

Notas
-----
- La curva se crea como malla (vértices + aristas), no como objeto Curve de Blender.
- Esto es intencional: se enfatiza el muestreo discreto.
"""

import bpy
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab03_3_1_ExplicitCurveMesh"

# -----------------------------
# Parámetros editables
# -----------------------------
X_MIN = -3.0
X_MAX =  3.0
N_SAMPLES = 120

def f(x: float) -> float:
    """Función explícita: y = f(x). Sustituir libremente."""
    return math.sin(2.0 * x) + 0.2 * x


# -----------------------------
# Limpieza escena (estándar del repo)
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
    # Curvas (si en el futuro añadimos HUDs aquí)
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
# Construcción de la malla
# -----------------------------
def build_polyline_mesh(points: list[Vector], name: str) -> bpy.types.Object:
    """
    Crea un mesh con vértices en 'points' y aristas conectando i->i+1.
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)

    verts = [(p.x, p.y, p.z) for p in points]
    edges = [(i, i + 1) for i in range(len(points) - 1)]
    faces = []

    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    return obj


def sample_explicit_curve(x_min: float, x_max: float, n: int) -> list[Vector]:
    if n < 2:
        raise ValueError("N_SAMPLES debe ser >= 2")

    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = x_min + t * (x_max - x_min)
        y = f(x)
        pts.append(Vector((x, y, 0.0)))
    return pts


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    pts = sample_explicit_curve(X_MIN, X_MAX, N_SAMPLES)
    curve_obj = build_polyline_mesh(pts, "ExplicitCurve")

    bpy.context.scene.collection.objects.link(curve_obj)
    move_object_to_collection_only(curve_obj, col)

    # Selección para comodidad
    bpy.ops.object.select_all(action="DESELECT")
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj

    print("=== Lab 03.3.1 — Curva explícita y=f(x) (mesh) ===")
    print("La escena previa ha sido eliminada.")
    print(f"Rango x: [{X_MIN}, {X_MAX}]")
    print(f"Muestras: {N_SAMPLES}")
    print("Objeto creado: ExplicitCurve (mesh con aristas).")
    print("Sugerencia: edita f(x), rango o N_SAMPLES y re-ejecuta.")


if __name__ == "__main__":
    main()


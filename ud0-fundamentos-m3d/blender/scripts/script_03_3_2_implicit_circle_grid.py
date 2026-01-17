"""
Lab 03.3.2 — Curva implícita: círculo como F(x,y)=0 (muestreo en rejilla)
========================================================================

Objetivo
--------
Construir una representación discreta de una curva implícita usando un test:
    F(x, y) = 0

Ejemplo: circunferencia de radio R
    F(x, y) = x^2 + y^2 - R^2

Estrategia (muestreo)
---------------------
1) Crear una rejilla de puntos (x_i, y_j) en un rango.
2) Seleccionar aquellos que cumplen:
       |F(x, y)| < EPS
3) Mostrar el resultado como una nube de puntos.

Concepto clave
--------------
- En implícita, la ecuación define pertenencia ("este punto está en la curva").
- No hay un parámetro u que recorra la curva, por eso el conjunto no está ordenado.
- Conectar puntos para formar una polilínea requiere un algoritmo adicional
  (p.ej. marching squares), que NO es el objetivo de este ejercicio.

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crea un mesh "ImplicitCirclePoints" con vértices (sin aristas).
3) Ajustar parámetros:
   - R (radio)
   - GRID_RES (densidad)
   - EPS (tolerancia)
   y re-ejecutar para ver diferencias.

Mini-diagrama ASCII
-------------------
Test de pertenencia:
  F(x,y) = x^2 + y^2 - R^2

(x,y) está "cerca" de la curva si |F(x,y)| < EPS
"""

import bpy
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab03_3_2_ImplicitCircle"

# -----------------------------
# Parámetros editables
# -----------------------------
R = 2.0
GRID_MIN = -2.5
GRID_MAX =  2.5
GRID_RES = 140     # número de muestras por eje (más -> más puntos)
EPS = 0.04         # tolerancia del test |F(x,y)| < EPS


def F(x: float, y: float) -> float:
    """Función implícita del círculo: F(x,y)=0."""
    return x*x + y*y - R*R


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
# Construcción: nube de puntos
# -----------------------------
def sample_implicit_points() -> list[Vector]:
    if GRID_RES < 2:
        raise ValueError("GRID_RES debe ser >= 2")

    pts = []
    for i in range(GRID_RES):
        tx = i / (GRID_RES - 1)
        x = GRID_MIN + tx * (GRID_MAX - GRID_MIN)
        for j in range(GRID_RES):
            ty = j / (GRID_RES - 1)
            y = GRID_MIN + ty * (GRID_MAX - GRID_MIN)

            val = F(x, y)
            if abs(val) < EPS:
                pts.append(Vector((x, y, 0.0)))

    return pts


def build_point_cloud_mesh(points: list[Vector], name: str) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)

    verts = [(p.x, p.y, p.z) for p in points]
    edges = []
    faces = []

    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    return obj


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    pts = sample_implicit_points()
    cloud_obj = build_point_cloud_mesh(pts, "ImplicitCirclePoints")

    bpy.context.scene.collection.objects.link(cloud_obj)
    move_object_to_collection_only(cloud_obj, col)

    bpy.ops.object.select_all(action="DESELECT")
    cloud_obj.select_set(True)
    bpy.context.view_layer.objects.active = cloud_obj

    print("=== Lab 03.3.2 — Curva implícita (círculo) ===")
    print("La escena previa ha sido eliminada.")
    print(f"F(x,y) = x^2 + y^2 - R^2  con R = {R}")
    print(f"GRID_RES = {GRID_RES}   EPS = {EPS}")
    print(f"Puntos seleccionados: {len(pts)}")
    print("Objeto creado: ImplicitCirclePoints (mesh solo con vértices).")
    print("Sugerencia: cambia GRID_RES o EPS y re-ejecuta para ver el efecto.")


if __name__ == "__main__":
    main()


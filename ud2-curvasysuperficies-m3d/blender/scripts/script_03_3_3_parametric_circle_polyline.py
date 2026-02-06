"""
Lab 03.3.3 — Curva paramétrica: círculo P(u) (polilínea ordenada)
=================================================================

Objetivo
--------
Construir un círculo mediante una formulación paramétrica:
    P(u) = (x(u), y(u), z(u)),  u ∈ [0, 1]

Para un círculo de radio R en el plano XY:
    x(u) = R cos(2πu)
    y(u) = R sin(2πu)
    z(u) = 0

Concepto clave
--------------
- Formulación paramétrica: el parámetro u "recorre" la curva en orden.
- Esto hace natural:
  - generar puntos ordenados,
  - conectar puntos consecutivos,
  - cerrar la curva.

Comparación con implícita (3.2)
-------------------------------
- Implícita: test de pertenencia |F(x,y)|<EPS sobre rejilla -> puntos NO ordenados.
- Paramétrica: muestreo en u -> puntos ordenados -> polilínea "limpia".

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crea "ParametricCircle" como mesh (vértices + aristas) y se cierra la polilínea.
3) Modificar parámetros (R, N_SAMPLES, TWOPI_FACTOR) y re-ejecutar.

Mini-diagrama ASCII
-------------------
u: 0 -----> 1
     recorre el círculo en sentido antihorario (si TWOPI_FACTOR > 0)

Puntos conectados en orden: (0)->(1)->...->(n-1)->(0)
"""

import bpy
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab03_3_3_ParametricCircle"

# -----------------------------
# Parámetros editables
# -----------------------------
R = 2.0
N_SAMPLES = 128          # más muestras -> mejor aproximación
TWOPI_FACTOR = 1.0       # 1.0 => círculo completo; 0.5 => media vuelta; 2.0 => dos vueltas


def P(u: float) -> Vector:
    """P(u) para el círculo en XY."""
    angle = (2.0 * math.pi * TWOPI_FACTOR) * u
    return Vector((R * math.cos(angle), R * math.sin(angle), 0.0))


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
# Construcción de polilínea cerrada
# -----------------------------
def sample_parametric_curve(n: int) -> list[Vector]:
    if n < 3:
        raise ValueError("N_SAMPLES debe ser >= 3 para cerrar una curva de forma útil.")

    pts = []
    for i in range(n):
        u = i / n  # ojo: usamos n, no (n-1), para evitar duplicar el punto inicial
        pts.append(P(u))
    return pts


def build_closed_polyline_mesh(points: list[Vector], name: str) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)

    verts = [(p.x, p.y, p.z) for p in points]
    edges = [(i, i + 1) for i in range(len(points) - 1)]
    edges.append((len(points) - 1, 0))  # cerrar

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

    pts = sample_parametric_curve(N_SAMPLES)
    obj = build_closed_polyline_mesh(pts, "ParametricCircle")

    bpy.context.scene.collection.objects.link(obj)
    move_object_to_collection_only(obj, col)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print("=== Lab 03.3.3 — Curva paramétrica (círculo) ===")
    print("La escena previa ha sido eliminada.")
    print(f"R = {R}")
    print(f"N_SAMPLES = {N_SAMPLES}")
    print(f"TWOPI_FACTOR = {TWOPI_FACTOR}")
    print("Objeto creado: ParametricCircle (mesh con aristas, cerrado).")
    print("Sugerencia: cambia N_SAMPLES para ver el efecto en la aproximación.")


if __name__ == "__main__":
    main()


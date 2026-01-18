"""
Lab 05.5.1 — Polinomios de Bernstein cúbicos: B0..B3 y suma
===========================================================

Objetivo
--------
Visualizar los 4 polinomios de Bernstein de grado 3 sobre u ∈ [0,1] y comprobar:

- B0(u) = (1-u)^3
- B1(u) = 3u(1-u)^2
- B2(u) = 3u^2(1-u)
- B3(u) = u^3

Propiedad fundamental:
- Para todo u ∈ [0,1], B0(u)+B1(u)+B2(u)+B3(u) = 1

Interpretación (para Bézier)
----------------------------
Los Bernstein funcionan como "pesos" (no negativos en [0,1]) cuya suma es 1.
Esto hace que una combinación Σ Pi Bi(u) sea una combinación convexa:
el punto P(u) queda en el "entorno" del polígono de control.

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Se crean 5 polilíneas (mesh):
   - B0_curve, B1_curve, B2_curve, B3_curve, Sum_curve
3) Ejes del gráfico:
   - x = u * X_SCALE
   - y = Bk(u) * Y_SCALE

Nota
----
No se usa LaTeX en el viewport. El HUD muestra el error máximo de la suma.
"""

import bpy
import blf
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab05_5_1_Bernstein"

# Muestreo
N_SAMPLES = 200

# Escala del "gráfico" en el espacio 3D
X_SCALE = 6.0
Y_SCALE = 3.0

# HUD
_HANDLER_KEY = "LAB05_5_1_BERNSTEIN_DRAW_HANDLER"
_TIMER_KEY = "LAB05_5_1_BERNSTEIN_TIMER_REGISTERED"

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
]

# -----------------------------
# Limpieza HUD
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
# Bernstein
# -----------------------------
def B0(u: float) -> float:
    return (1.0 - u) ** 3

def B1(u: float) -> float:
    return 3.0 * u * (1.0 - u) ** 2

def B2(u: float) -> float:
    return 3.0 * (u ** 2) * (1.0 - u)

def B3(u: float) -> float:
    return u ** 3

# -----------------------------
# Mesh polilínea
# -----------------------------
def build_polyline_mesh(points: list[Vector], name: str) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    verts = [(p.x, p.y, p.z) for p in points]
    edges = [(i, i + 1) for i in range(len(points) - 1)]
    faces = []
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    return obj

def sample_curve(f, z_offset: float) -> list[Vector]:
    pts = []
    for i in range(N_SAMPLES):
        u = i / (N_SAMPLES - 1)
        x = u * X_SCALE
        y = f(u) * Y_SCALE
        pts.append(Vector((x, y, z_offset)))
    return pts

# -----------------------------
# HUD
# -----------------------------
def _draw_text(x: int, y: int, text: str, size: int = 14) -> None:
    font_id = 0
    ui_scale = bpy.context.preferences.system.ui_scale
    blf.size(font_id, int(size * ui_scale))
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)

def _hud_draw_callback() -> None:
    x0, y0 = 20, 140
    line = 18

    _draw_text(x0, y0 + 4 * line, "Lab 05.5.1 — Bernstein cúbico (B0..B3) y suma", size=16)

    err = bpy.app.driver_namespace.get("LAB05_5_1_SUM_ERR", None)
    if err is None:
        _draw_text(x0, y0 + 3 * line, "Estado: sin error calculado (ejecutar el script).", size=13)
        return

    _draw_text(x0, y0 + 3 * line, "Propiedad: B0+B1+B2+B3 = 1 para u en [0,1]", size=13)
    _draw_text(x0, y0 + 2 * line, f"Error máximo muestreado |(suma - 1)| = {err:.6e}", size=13)
    _draw_text(x0, y0 + 1 * line, f"Muestras: {N_SAMPLES}   Escalas: X={X_SCALE}, Y={Y_SCALE}", size=13)
    _draw_text(x0, y0 + 0 * line, "En el siguiente ejercicio: P(u)=Σ Pi Bi(u) (Bézier cúbica)", size=13)

def _install_hud_handler() -> None:
    remove_all_known_lab_handlers()
    handler = bpy.types.SpaceView3D.draw_handler_add(_hud_draw_callback, (), "WINDOW", "POST_PIXEL")
    bpy.app.driver_namespace[_HANDLER_KEY] = handler

def _tag_redraw_all_3dviews() -> None:
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    # Curvas a distintas "capas" z para distinguir visualmente sin colores
    curves = [
        ("B0_curve", B0, 0.00),
        ("B1_curve", B1, 0.15),
        ("B2_curve", B2, 0.30),
        ("B3_curve", B3, 0.45),
        ("Sum_curve", lambda u: B0(u) + B1(u) + B2(u) + B3(u), 0.60),
    ]

    max_err = 0.0
    for name, f, z in curves:
        pts = sample_curve(f, z)
        obj = build_polyline_mesh(pts, name)
        bpy.context.scene.collection.objects.link(obj)
        move_object_to_collection_only(obj, col)

        if name == "Sum_curve":
            # calcular error máximo
            for i in range(N_SAMPLES):
                u = i / (N_SAMPLES - 1)
                s = B0(u) + B1(u) + B2(u) + B3(u)
                max_err = max(max_err, abs(s - 1.0))

    bpy.app.driver_namespace["LAB05_5_1_SUM_ERR"] = max_err

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    print("=== Lab 05.5.1 — Bernstein cúbico ===")
    print("La escena previa ha sido eliminada.")
    print(f"Error máximo muestreado |(suma - 1)| = {max_err:.6e}")
    print("Objetos creados: B0_curve, B1_curve, B2_curve, B3_curve, Sum_curve")

if __name__ == "__main__":
    main()


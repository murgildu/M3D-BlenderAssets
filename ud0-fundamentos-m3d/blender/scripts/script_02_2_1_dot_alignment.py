"""
Lab 02.2.1 — Producto escalar como medidor de alineamiento (con HUD)
====================================================================

Objetivo
--------
Visualizar cómo el producto escalar (dot) mide el alineamiento entre dos direcciones unitarias u y v:

- dot(u, v) = cos(theta)  si u y v están normalizados
- theta = arccos(dot(u, v))

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Rotar el objeto "V_dir" (R). Sus flechas representan su eje Y local (dirección v).
3) El objeto "U_ref" es la dirección de referencia (u), fija (eje Y local).
4) El HUD muestra:
   - dot(u, v)
   - ángulo(theta) en grados

Interpretación
--------------
- dot ~ 1   -> direcciones casi iguales (theta ~ 0°)
- dot ~ 0   -> direcciones perpendiculares (theta ~ 90°)
- dot ~ -1  -> direcciones opuestas (theta ~ 180°)
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab02_2_1_DotAlignment"

_HANDLER_KEY = "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER"
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
]


# -----------------------------
# HUD handlers: limpieza
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
# Limpieza total de escena
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
# Cálculo de ejes locales
# -----------------------------
def world_local_y_axis(obj: bpy.types.Object) -> Vector:
    """Eje Y local del objeto expresado en coordenadas globales."""
    return (obj.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


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
    x0, y0 = 20, 130
    line = 18

    _draw_text(x0, y0 + 5 * line, "Lab 02.2.1 — Dot product (alineamiento)", size=16)
    _draw_text(x0, y0 + 4 * line, "Acción: rotar 'V_dir' (R) y observar dot y ángulo", size=13)

    U = bpy.data.objects.get("U_ref")
    V = bpy.data.objects.get("V_dir")
    if U is None or V is None:
        _draw_text(x0, y0 + 3 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    u = world_local_y_axis(U)
    v = world_local_y_axis(V)

    dot = clamp(u.dot(v), -1.0, 1.0)
    ang_deg = math.degrees(math.acos(dot))

    _draw_text(x0, y0 + 3 * line, f"u (Y local de U_ref) = ({u.x:.3f}, {u.y:.3f}, {u.z:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"v (Y local de V_dir) = ({v.x:.3f}, {v.y:.3f}, {v.z:.3f})", size=13)
    _draw_text(x0, y0 + 1 * line, f"dot(u,v) = {dot:.4f}   (cos(theta))", size=13)
    _draw_text(x0, y0 + 0 * line, f"theta = arccos(dot) = {ang_deg:.2f}°", size=13)


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
# Creación de escena
# -----------------------------
def create_scene_demo() -> None:
    col = ensure_collection(LAB_COLLECTION_NAME)

    U = bpy.data.objects.new("U_ref", None)
    U.empty_display_type = "ARROWS"
    U.empty_display_size = 0.4
    U.location = Vector((0.0, 0.0, 0.0))
    col.objects.link(U)

    V = bpy.data.objects.new("V_dir", None)
    V.empty_display_type = "ARROWS"
    V.empty_display_size = 0.4
    V.location = Vector((2.0, 0.0, 0.0))
    col.objects.link(V)

    move_object_to_collection_only(U, col)
    move_object_to_collection_only(V, col)

    bpy.ops.object.select_all(action="DESELECT")
    V.select_set(True)
    bpy.context.view_layer.objects.active = V


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()
    create_scene_demo()

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    print("=== Lab 02.2.1 — Dot product (alineamiento) ===")
    print("La escena previa ha sido eliminada.")
    print("Objetos creados: U_ref (referencia), V_dir (rotar).")
    print("Acción: rota V_dir (R) y observa dot y ángulo en el HUD.")


if __name__ == "__main__":
    main()


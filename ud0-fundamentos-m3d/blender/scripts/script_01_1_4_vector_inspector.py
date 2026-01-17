"""
Lab 01.1.4 — Inspector de Vectores (con HUD)
============================================

Objetivo
--------
Para dos objetos A y B se calcula:
- d = B.location - A.location  y  |d|
- YA: eje Y local de A expresado en mundo
- YB: eje Y local de B expresado en mundo
- dot(YA, YB)
- ángulo(YA, YB) en grados

Guía UI
-------
1) Ejecutar este script:
   - elimina toda la escena previa (incluyendo objetos por defecto y restos de otros labs)
   - crea A y B como empties tipo ARROWS
   - activa HUD
2) Acciones:
   - Rotar A/B (R): observar dot y ángulo
   - Mover B (G): observar d y |d|

Nota (HUD persistente)
----------------------
Los HUDs se implementan con draw handlers y pueden persistir durante la sesión de Blender.
Este script elimina HUDs previos conocidos antes de instalar el suyo.
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab01_1_4_VectorInspector"

_HANDLER_KEY = "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER"
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
]


# -----------------------------
# Limpieza de HUDs persistentes
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
# Colecciones utilitarias
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
# Cálculos
# -----------------------------
def world_local_y_axis(obj: bpy.types.Object) -> Vector:
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

    _draw_text(x0, y0 + 6 * line, "Lab 01.1.4 — Inspector de Vectores", size=16)
    _draw_text(x0, y0 + 5 * line, "Acción: rotar A/B (R) y mover B (G)", size=13)

    A = bpy.data.objects.get("A")
    B = bpy.data.objects.get("B")
    if A is None or B is None:
        _draw_text(x0, y0 + 4 * line, "Estado: objetos A/B no encontrados (ejecutar el script).", size=13)
        return

    a_loc = Vector(A.location)
    b_loc = Vector(B.location)
    d = b_loc - a_loc
    dist = d.length

    YA = world_local_y_axis(A)
    YB = world_local_y_axis(B)

    dot = clamp(YA.dot(YB), -1.0, 1.0)
    ang_deg = math.degrees(math.acos(dot))

    _draw_text(x0, y0 + 4 * line, f"A.location = ({a_loc.x:.3f}, {a_loc.y:.3f}, {a_loc.z:.3f})", size=13)
    _draw_text(x0, y0 + 3 * line, f"B.location = ({b_loc.x:.3f}, {b_loc.y:.3f}, {b_loc.z:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"d = B - A = ({d.x:.3f}, {d.y:.3f}, {d.z:.3f})   |d| = {dist:.4f}", size=13)
    _draw_text(x0, y0 + 1 * line, f"dot(YA,YB) = {dot:.4f}", size=13)
    _draw_text(x0, y0 + 0 * line, f"ángulo(YA,YB) = {ang_deg:.2f}°", size=13)


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
# Creación de escena demo
# -----------------------------
def create_scene_demo() -> None:
    col = ensure_collection(LAB_COLLECTION_NAME)

    A = bpy.data.objects.new("A", None)
    A.empty_display_type = "ARROWS"
    A.empty_display_size = 0.35
    A.location = Vector((0.0, 0.0, 0.0))
    col.objects.link(A)

    B = bpy.data.objects.new("B", None)
    B.empty_display_type = "ARROWS"
    B.empty_display_size = 0.35
    B.location = Vector((2.0, 1.0, 0.0))
    col.objects.link(B)

    move_object_to_collection_only(A, col)
    move_object_to_collection_only(B, col)

    bpy.ops.object.select_all(action="DESELECT")
    A.select_set(True)
    B.select_set(True)
    bpy.context.view_layer.objects.active = B


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    wipe_scene()
    create_scene_demo()

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    print("=== Lab 01.1.4 — Inspector de Vectores ===")
    print("HUDs previos eliminados (si existían).")
    print("La escena previa ha sido eliminada.")
    print("Objetos creados: A y B (empties tipo ARROWS).")
    print("Acción: rotar A/B (R) y mover B (G).")


if __name__ == "__main__":
    main()


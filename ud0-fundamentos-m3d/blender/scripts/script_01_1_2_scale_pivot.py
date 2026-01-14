"""
Lab 01.1.2 — Escalado respecto a un pivote (con HUD en viewport)
===============================================================

IMPORTANTE (HUD persistente)
----------------------------
Los HUDs se implementan con draw handlers, que pueden persistir en la sesión de Blender
aunque se cargue un archivo .blend nuevo. Por ello, este script elimina cualquier HUD
previo de prácticas antes de instalar el suyo.

Modelo teórico
--------------
P' = C + k (P - C)

Guía UI
-------
1) Ejecutar este script (borra la escena, crea el laboratorio y activa el HUD).
2) Mover "P_user" (G) hasta coincidir con "P_target".
3) El HUD muestra error posicional y ratio radial respecto a C.
4) (Opcional) Ejecutar el checker: check_01_1_2_scale_pivot.py
"""

import bpy
import blf
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab01_1_2_ScalePivot"

# Parámetros del ejercicio
C_LOC = Vector((0.5, -0.5, 0.0))
P_LOC = Vector((2.0, 1.0, 0.0))
K_SCALE = 1.8

ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
ARROW_HEAD_LENGTH = 0.25

EPS_POS = 0.03
EPS_RATIO = 0.05

_HANDLER_KEY = "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER"

# Lista global de handlers conocidos (para limpiar HUDs de otros ejercicios)
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
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
# Colecciones y creación segura
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


def create_empty_in_collection(
    col: bpy.types.Collection,
    name: str,
    location: Vector,
    display: str = "SPHERE",
    size: float = 0.25,
) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = display
    empty.empty_display_size = size
    empty.location = location
    col.objects.link(empty)
    return empty


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
    if direction.length < 1e-9:
        return
    d = direction.normalized()
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = z_axis.rotation_difference(d)


def create_vector_arrow(col: bpy.types.Collection, name: str, start: Vector, vec: Vector) -> bpy.types.Object:
    length = vec.length
    if length < 1e-9:
        return create_empty_in_collection(col, name, start, display="ARROWS", size=0.4)

    arrow_root = bpy.data.objects.new(name, None)
    arrow_root.empty_display_type = "PLAIN_AXES"
    arrow_root.location = start
    col.objects.link(arrow_root)

    shaft_len = max(0.0, length - ARROW_HEAD_LENGTH)
    head_len = min(ARROW_HEAD_LENGTH, length)

    shaft = create_cylinder(f"{name}_shaft", ARROW_SHAFT_RADIUS, shaft_len)
    head = create_cone(f"{name}_head", ARROW_HEAD_RADIUS, head_len)

    move_object_to_collection_only(shaft, col)
    move_object_to_collection_only(head, col)

    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))

    shaft.parent = arrow_root
    head.parent = arrow_root

    orient_object_from_z_axis(arrow_root, vec)
    return arrow_root


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
    P_user = bpy.data.objects.get("P_user")
    P_target = bpy.data.objects.get("P_target")
    P = bpy.data.objects.get("P")
    C = bpy.data.objects.get("C_pivot")

    x0, y0 = 20, 92
    line = 18

    _draw_text(x0, y0 + 4 * line, "Lab 01.1.2 — Escalado respecto a pivote", size=16)
    _draw_text(x0, y0 + 3 * line, "Acción: mover 'P_user' hasta 'P_target' (tecla G)", size=13)
    _draw_text(x0, y0 + 2 * line, "Modelo: P' = C + k (P - C)", size=13)

    if any(o is None for o in (P_user, P_target, P, C)):
        _draw_text(x0, y0 + 1 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    err_pos = (Vector(P_user.location) - Vector(P_target.location)).length
    status_pos = "PASS" if err_pos < EPS_POS else "FAIL"

    d0 = (Vector(P.location) - Vector(C.location)).length
    d1 = (Vector(P_user.location) - Vector(C.location)).length
    ratio = (d1 / d0) if d0 > 1e-9 else float("inf")
    status_ratio = "PASS" if abs(ratio - K_SCALE) < EPS_RATIO else "FAIL"

    _draw_text(
        x0, y0 + 1 * line,
        f"Error posicional |P_user - P_target| = {err_pos:.4f}   (EPS_POS={EPS_POS:.3f})   {status_pos}",
        size=13
    )
    _draw_text(
        x0, y0 + 0 * line,
        f"Ratio distancias dist(C,P_user)/dist(C,P) = {ratio:.3f}   (k={K_SCALE:.3f}, EPS_RATIO={EPS_RATIO:.3f})   {status_ratio}",
        size=13
    )


def _install_hud_handler() -> None:
    # Limpia handlers conocidos (incluye el propio) para evitar solapes
    remove_all_known_lab_handlers()

    handler = bpy.types.SpaceView3D.draw_handler_add(_hud_draw_callback, (), "WINDOW", "POST_PIXEL")
    bpy.app.driver_namespace[_HANDLER_KEY] = handler


def _tag_redraw_all_3dviews() -> None:
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


# -----------------------------
# Lógica del ejercicio
# -----------------------------
def scale_point_about_pivot(P: Vector, C: Vector, k: float) -> Vector:
    return C + k * (P - C)


def main() -> None:
    # 1) Asegurar que no queda ningún HUD anterior activo
    remove_all_known_lab_handlers()

    # 2) Limpiar escena para reproducibilidad
    wipe_scene()

    # 3) Crear laboratorio
    col = ensure_collection(LAB_COLLECTION_NAME)

    P_target_loc = scale_point_about_pivot(P_LOC, C_LOC, K_SCALE)

    create_empty_in_collection(col, "C_pivot", C_LOC, display="ARROWS", size=0.30)
    bpy.context.scene.cursor.location = C_LOC
    bpy.context.scene["LAB01_1_2_K"] = float(K_SCALE)  # para checker parametrizable

    create_empty_in_collection(col, "P", P_LOC, display="SPHERE", size=0.22)
    create_empty_in_collection(col, "P_target", P_target_loc, display="CUBE", size=0.22)
    create_empty_in_collection(col, "P_user", P_LOC, display="SPHERE", size=0.26)

    create_vector_arrow(col, "k_vector", C_LOC, (P_target_loc - C_LOC))

    # 4) Activar HUD
    _install_hud_handler()
    _tag_redraw_all_3dviews()

    print("=== Lab 01.1.2 — Escalado respecto a pivote ===")
    print("HUDs previos eliminados (si existían).")
    print("La escena previa ha sido eliminada.")
    print(f"C (pivote) = {tuple(C_LOC)}")
    print(f"P          = {tuple(P_LOC)}")
    print(f"k          = {K_SCALE}")
    print(f"P_target   = {tuple(P_target_loc)}")
    print("Acción: mover 'P_user' hasta coincidir con 'P_target'.")
    print("Colección creada:", LAB_COLLECTION_NAME)


if __name__ == "__main__":
    main()


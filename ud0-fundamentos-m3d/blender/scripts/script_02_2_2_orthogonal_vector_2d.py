"""
Lab 02.2.2 — Ortogonalidad (2D): construir un vector perpendicular (con HUD)
============================================================================

Modelo teórico (en R^2)
----------------------
Dados u = (a, b), un vector perpendicular es:
    v = (-b, a)

Justificación rápida:
    u · v = (a, b) · (-b, a) = a(-b) + b(a) = -ab + ab = 0

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) El vector u está fijo en el plano XY, desde O hasta U_tip.
3) El vector v_ref es el perpendicular correcto (referencia), desde O hasta V_tip_target.
4) Acción del alumno:
   - mover "V_tip_user" (G) para que coincida con "V_tip_target"
5) El HUD muestra:
   - u, v_user (en XY)
   - dot(u, v_user)
   - ángulo
   - PASS/FAIL

Notas
-----
- El ejercicio se restringe al plano XY: z=0.
- Para evitar ambigüedad de escala, se usa v_perp con la misma longitud que u.
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab02_2_2_Orthogonal2D"

_HANDLER_KEY = "LAB02_2_2_ORTHO2D_DRAW_HANDLER"
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
]

# Parámetros del vector u en XY
U_VEC = Vector((2.0, 1.0, 0.0))  # u = (a,b)
O_LOC = Vector((0.0, 0.0, 0.0))

# Flechas (actualizables)
ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
UNIT_ARROW_HEAD_FRAC = 0.25

# Tolerancias
EPS_POS = 0.05   # para coincidir V_tip_user con V_tip_target
EPS_DOT = 0.05   # para dot ≈ 0
EPS_NONZERO = 1e-6

# Timer
_TIMER_KEY = "LAB02_2_2_TIMER_REGISTERED"


# -----------------------------
# Limpieza HUD persistente
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


def create_empty_in_collection(col, name, location, display="SPHERE", size=0.25) -> bpy.types.Object:
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
    if direction.length < 1e-12:
        return
    d = direction.normalized()
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = z_axis.rotation_difference(d)


# -----------------------------
# Flecha actualizable
# -----------------------------
def create_unit_arrow(col, base_name: str, start: Vector) -> dict:
    root = bpy.data.objects.new(base_name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.location = start
    col.objects.link(root)

    shaft = create_cylinder(f"{base_name}_shaft", ARROW_SHAFT_RADIUS, 1.0)
    head = create_cone(f"{base_name}_head", ARROW_HEAD_RADIUS, 1.0)

    move_object_to_collection_only(shaft, col)
    move_object_to_collection_only(head, col)

    shaft.parent = root
    head.parent = root
    return {"root": root, "shaft": shaft, "head": head}


def update_arrow(arrow: dict, start: Vector, vec: Vector) -> None:
    root, shaft, head = arrow["root"], arrow["shaft"], arrow["head"]
    root.location = start

    L = vec.length
    if L < 1e-9:
        shaft.scale = Vector((1.0, 1.0, 0.0001))
        head.scale = Vector((1.0, 1.0, 0.0001))
        shaft.location = Vector((0.0, 0.0, 0.0))
        head.location = Vector((0.0, 0.0, 0.0))
        return

    orient_object_from_z_axis(root, vec)

    head_len = max(0.05, min(L * UNIT_ARROW_HEAD_FRAC, 0.4))
    shaft_len = max(0.001, L - head_len)

    shaft.scale = Vector((1.0, 1.0, shaft_len))
    head.scale = Vector((1.0, 1.0, head_len))

    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))


# -----------------------------
# Matemática del ejercicio
# -----------------------------
def perp_2d(u: Vector) -> Vector:
    """Devuelve un perpendicular en XY: (-b, a), con z=0."""
    return Vector((-u.y, u.x, 0.0))


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
    x0, y0 = 20, 140
    line = 18

    _draw_text(x0, y0 + 6 * line, "Lab 02.2.2 — Ortogonalidad (2D): construir v ⟂ u", size=16)
    _draw_text(x0, y0 + 5 * line, "Acción: mover 'V_tip_user' (G) hasta 'V_tip_target'", size=13)
    _draw_text(x0, y0 + 4 * line, "Referencia: v = (-b, a) si u = (a, b)", size=13)

    O = bpy.data.objects.get("O")
    U_tip = bpy.data.objects.get("U_tip")
    V_tip_user = bpy.data.objects.get("V_tip_user")
    V_tip_target = bpy.data.objects.get("V_tip_target")

    if any(o is None for o in (O, U_tip, V_tip_user, V_tip_target)):
        _draw_text(x0, y0 + 3 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    o = Vector(O.location)
    u = Vector(U_tip.location) - o
    v_user = Vector(V_tip_user.location) - o

    # restringir a XY (informativo)
    u2 = Vector((u.x, u.y, 0.0))
    v2 = Vector((v_user.x, v_user.y, 0.0))

    if u2.length < EPS_NONZERO or v2.length < EPS_NONZERO:
        _draw_text(x0, y0 + 3 * line, "Estado: vector nulo (evitar u=0 o v=0).", size=13)
        return

    dot = u2.dot(v2)
    # ángulo entre direcciones
    dot_n = clamp(u2.normalized().dot(v2.normalized()), -1.0, 1.0)
    ang_deg = math.degrees(math.acos(dot_n))

    err_pos = (Vector(V_tip_user.location) - Vector(V_tip_target.location)).length
    ok_pos = err_pos < EPS_POS
    ok_dot = abs(dot) < EPS_DOT * u2.length * v2.length  # tolerancia proporcional al tamaño
    status = "PASS" if (ok_pos and ok_dot) else "FAIL"

    _draw_text(x0, y0 + 3 * line, f"u = ({u2.x:.3f}, {u2.y:.3f})    v_user = ({v2.x:.3f}, {v2.y:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"u·v_user = {dot:.4f}    ángulo = {ang_deg:.2f}°", size=13)
    _draw_text(x0, y0 + 1 * line, f"error_pos = dist(V_tip_user, V_tip_target) = {err_pos:.4f}   (EPS_POS={EPS_POS:.3f})", size=13)
    _draw_text(x0, y0 + 0 * line, f"Condición ortogonalidad: u·v ≈ 0   Estado = {status}", size=13)


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
# Timer: actualizar flechas/target
# -----------------------------
def _unregister_timer_if_needed():
    ns = bpy.app.driver_namespace
    if ns.get(_TIMER_KEY, False):
        if bpy.app.timers.is_registered(_update_scene):
            try:
                bpy.app.timers.unregister(_update_scene)
            except Exception:
                pass
        ns[_TIMER_KEY] = False


def _update_scene():
    O = bpy.data.objects.get("O")
    U_tip = bpy.data.objects.get("U_tip")
    V_tip_target = bpy.data.objects.get("V_tip_target")

    if any(x is None for x in (O, U_tip, V_tip_target)):
        return 0.1

    o = Vector(O.location)
    u = Vector(U_tip.location) - o
    u2 = Vector((u.x, u.y, 0.0))

    # target perpendicular con misma longitud que u
    if u2.length < EPS_NONZERO:
        V_tip_target.location = o
    else:
        v = perp_2d(u2).normalized() * u2.length
        V_tip_target.location = o + v

    # actualizar flechas si existen
    arrow_u = bpy.app.driver_namespace.get("LAB02_2_2_ARROW_U")
    arrow_vref = bpy.app.driver_namespace.get("LAB02_2_2_ARROW_VREF")
    arrow_vuser = bpy.app.driver_namespace.get("LAB02_2_2_ARROW_VUSER")
    V_tip_user = bpy.data.objects.get("V_tip_user")

    if arrow_u is not None:
        update_arrow(arrow_u, o, u2)
    if arrow_vref is not None:
        update_arrow(arrow_vref, o, Vector(V_tip_target.location) - o)
    if arrow_vuser is not None and V_tip_user is not None:
        update_arrow(arrow_vuser, o, Vector(V_tip_user.location) - o)

    _tag_redraw_all_3dviews()
    return 0.05


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    _unregister_timer_if_needed()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    # Guardar tolerancias para el checker
    bpy.context.scene["LAB02_2_2_EPS_POS"] = float(EPS_POS)
    bpy.context.scene["LAB02_2_2_EPS_DOT"] = float(EPS_DOT)

    # Puntos
    create_empty_in_collection(col, "O", O_LOC, display="ARROWS", size=0.25)
    create_empty_in_collection(col, "U_tip", O_LOC + U_VEC, display="CUBE", size=0.22)

    # Target perpendicular (se calculará y actualizará por timer)
    create_empty_in_collection(col, "V_tip_target", O_LOC + perp_2d(U_VEC), display="CUBE", size=0.22)

    # Tip editable del alumno (se inicia lejos del target para no empezar en PASS)
    create_empty_in_collection(col, "V_tip_user", O_LOC + Vector((1.0, -1.5, 0.0)), display="SPHERE", size=0.28)

    # Flechas actualizables
    arrow_u = create_unit_arrow(col, "u_arrow", O_LOC)
    arrow_vref = create_unit_arrow(col, "v_ref_arrow", O_LOC)
    arrow_vuser = create_unit_arrow(col, "v_user_arrow", O_LOC)

    bpy.app.driver_namespace["LAB02_2_2_ARROW_U"] = arrow_u
    bpy.app.driver_namespace["LAB02_2_2_ARROW_VREF"] = arrow_vref
    bpy.app.driver_namespace["LAB02_2_2_ARROW_VUSER"] = arrow_vuser

    # Inicializar flechas
    update_arrow(arrow_u, O_LOC, U_VEC)
    update_arrow(arrow_vref, O_LOC, perp_2d(U_VEC))
    update_arrow(arrow_vuser, O_LOC, Vector((1.0, -1.5, 0.0)))

    # HUD + timer
    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    print("=== Lab 02.2.2 — Ortogonalidad (2D) ===")
    print("La escena previa ha sido eliminada.")
    print("Acción: mover 'V_tip_user' (G) hasta 'V_tip_target'.")
    print("El HUD muestra u·v y el ángulo (objetivo: u·v ≈ 0).")


if __name__ == "__main__":
    main()


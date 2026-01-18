"""
Lab 06.6.1 — Splines y continuidad: C0, G1 y C1 en un empalme Bézier
====================================================================

Fix importante:
--------------
Para que el modo funcione en ambos sentidos (0<->1<->2), el script guarda
una configuración base (C0) del empalme al crear la escena. Al volver a modo 0,
restaura esa configuración base.

Guía UI
-------
- Seleccionar "ContinuityControl"
- Object Properties -> Custom Properties -> mode:
    0 = C0
    1 = G1
    2 = C1
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab06_6_1_Continuity"

_HANDLER_KEY = "LAB06_6_1_CONTINUITY_DRAW_HANDLER"
_TIMER_KEY = "LAB06_6_1_CONTINUITY_TIMER_REGISTERED"

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

EPS = 1e-12


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


# -----------------------------
# Control empty con propiedades
# -----------------------------
def ensure_control_empty(col) -> bpy.types.Object:
    ctrl = bpy.data.objects.new("ContinuityControl", None)
    ctrl.empty_display_type = "CUBE"
    ctrl.empty_display_size = 0.25
    ctrl.location = Vector((0.0, -3.0, 0.0))
    col.objects.link(ctrl)

    # 0=C0, 1=G1, 2=C1
    ctrl["mode"] = 0

    # Almacenamiento de handles base en propiedades (se rellena luego)
    # ctrl["base_hl"] = (x,y,z)
    # ctrl["base_hr"] = (x,y,z)

    return ctrl


# -----------------------------
# Crear spline con 3 puntos: P0, J, P3
# -----------------------------
def create_bezier_spline() -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name="SplineContinuity_Data", type="CURVE")
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

    # Handles iniciales (C0 intencional: esquina)
    bp0.handle_right = P0 + Vector((0.8, 1.2, 0.0))
    bp1.handle_left  = J  + Vector((-0.8, -1.2, 0.0))  # esquina clara
    bp1.handle_right = J  + Vector((0.8, 0.0, 0.0))
    bp2.handle_left  = P3 + Vector((-0.8, 0.0, 0.0))

    obj = bpy.data.objects.new("SplineContinuity", curve_data)
    return obj


# -----------------------------
# Medición de tangentes en el empalme J
# -----------------------------
def tangent_left_at_join(spline) -> Vector:
    bp1 = spline.bezier_points[1]
    return 3.0 * (bp1.co - bp1.handle_left)

def tangent_right_at_join(spline) -> Vector:
    bp1 = spline.bezier_points[1]
    return 3.0 * (bp1.handle_right - bp1.co)

def angle_between(u: Vector, v: Vector) -> float:
    if u.length < EPS or v.length < EPS:
        return 0.0
    d = max(-1.0, min(1.0, u.normalized().dot(v.normalized())))
    return math.degrees(math.acos(d))


# -----------------------------
# Guardar / restaurar base C0
# -----------------------------
def store_base_handles(ctrl: bpy.types.Object, spline) -> None:
    """Guarda handles del empalme (bp1) como referencia C0."""
    bp1 = spline.bezier_points[1]
    hl = bp1.handle_left.copy()
    hr = bp1.handle_right.copy()
    ctrl["base_hl"] = (float(hl.x), float(hl.y), float(hl.z))
    ctrl["base_hr"] = (float(hr.x), float(hr.y), float(hr.z))

def restore_base_handles(ctrl: bpy.types.Object, spline) -> None:
    """Restaura handles base C0 si existen; si no, no hace nada."""
    if "base_hl" not in ctrl or "base_hr" not in ctrl:
        return
    bp1 = spline.bezier_points[1]
    bhl = Vector(ctrl["base_hl"])
    bhr = Vector(ctrl["base_hr"])
    bp1.handle_left = bhl
    bp1.handle_right = bhr


# -----------------------------
# Imposición de modos C0 / G1 / C1
# -----------------------------
def impose_mode(ctrl: bpy.types.Object, spline, mode: int) -> None:
    """
    Ajusta handles en el join (bp1) para cumplir el modo.
    - C0: restaura configuración base guardada.
    - G1: colinearidad (misma dirección), longitudes libres.
    - C1: colinearidad + misma longitud (handles simétricos).
    """
    bp1 = spline.bezier_points[1]

    if mode == 0:
        restore_base_handles(ctrl, spline)
        return

    # Vectores actuales desde J a los handles
    vL = bp1.handle_left - bp1.co
    vR = bp1.handle_right - bp1.co

    # Si degenerados, partir de base (si existe) para estabilidad
    if vL.length < EPS or vR.length < EPS:
        restore_base_handles(ctrl, spline)
        vL = bp1.handle_left - bp1.co
        vR = bp1.handle_right - bp1.co

    if vR.length < EPS:
        vR = Vector((1.0, 0.0, 0.0))
    dirR = vR.normalized()

    if mode == 1:
        # G1: misma dirección (colineal), longitudes conservadas
        lenL = max(EPS, vL.length)
        lenR = max(EPS, vR.length)
        bp1.handle_right = bp1.co + dirR * lenR
        bp1.handle_left  = bp1.co - dirR * lenL
        return

    if mode == 2:
        # C1: misma dirección + misma magnitud
        lenL = max(EPS, vL.length)
        lenR = max(EPS, vR.length)
        L = 0.5 * (lenL + lenR)
        bp1.handle_right = bp1.co + dirR * L
        bp1.handle_left  = bp1.co - dirR * L
        return


# -----------------------------
# HUD
# -----------------------------
def _draw_text(x: int, y: int, text: str, size: int = 14) -> None:
    font_id = 0
    ui_scale = bpy.context.preferences.system.ui_scale
    blf.size(font_id, int(size * ui_scale))
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)

def mode_name(mode: int) -> str:
    return {0: "C0 (posición)", 1: "G1 (dirección tangente)", 2: "C1 (tangente igual)"}.get(mode, "desconocido")

def _hud_draw_callback() -> None:
    x0, y0 = 20, 160
    line = 18

    _draw_text(x0, y0 + 6 * line, "Lab 06.6.1 — Continuidad en empalme Bézier (C0 / G1 / C1)", size=16)
    _draw_text(x0, y0 + 5 * line, "Control: ContinuityControl['mode'] = 0,1,2", size=13)

    ctrl = bpy.data.objects.get("ContinuityControl")
    obj = bpy.data.objects.get("SplineContinuity")
    if ctrl is None or obj is None or obj.type != "CURVE":
        _draw_text(x0, y0 + 4 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)
    lenL = TL.length
    lenR = TR.length
    rel = abs(lenL - lenR) / max(EPS, (0.5 * (lenL + lenR)))

    _draw_text(x0, y0 + 4 * line, f"Modo actual: {mode} -> {mode_name(mode)}", size=13)
    _draw_text(x0, y0 + 3 * line, f"Ángulo entre tangentes en el empalme: {ang:.3f} grados", size=13)
    _draw_text(x0, y0 + 2 * line, f"|T_left| = {lenL:.4f}   |T_right| = {lenR:.4f}", size=13)
    _draw_text(x0, y0 + 1 * line, f"Diferencia relativa de magnitud: {rel:.4f}", size=13)
    _draw_text(x0, y0 + 0 * line, "G1: ángulo ~ 0 ; C1: ángulo ~ 0 y magnitudes ~ iguales", size=13)

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
# Timer
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
    ctrl = bpy.data.objects.get("ContinuityControl")
    obj = bpy.data.objects.get("SplineContinuity")
    if ctrl is None or obj is None or obj.type != "CURVE":
        return 0.2

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    impose_mode(ctrl, spline, mode)

    _tag_redraw_all_3dviews()
    return 0.10


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    _unregister_timer_if_needed()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    ctrl = ensure_control_empty(col)
    move_object_to_collection_only(ctrl, col)

    curve_obj = create_bezier_spline()
    bpy.context.scene.collection.objects.link(curve_obj)
    move_object_to_collection_only(curve_obj, col)

    # Guardar configuración base C0 del join
    spline = curve_obj.data.splines[0]
    store_base_handles(ctrl, spline)

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    bpy.ops.object.select_all(action="DESELECT")
    ctrl.select_set(True)
    bpy.context.view_layer.objects.active = ctrl

    print("=== Lab 06.6.1 — Continuidad C0 / G1 / C1 ===")
    print("La escena previa ha sido eliminada.")
    print("Control: ContinuityControl['mode'] (0=C0, 1=G1, 2=C1)")
    print("Fix aplicado: modo 0 restaura handles base (funciona también al ir hacia atrás).")

if __name__ == "__main__":
    main()


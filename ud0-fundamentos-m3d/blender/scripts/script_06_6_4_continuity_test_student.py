"""
Lab 06.6.4 — El Test de Continuidad: construir G1 y C1 por ajuste de handles
============================================================================

Objetivo
--------
Implementar un ajuste de continuidad en un empalme Bézier manipulando handles.

En el empalme J (punto central), definimos:
- Tangente izquierda (al llegar a J desde el tramo previo):
    T_left = 3 (J - handle_left(J))

- Tangente derecha (al salir de J hacia el siguiente tramo):
    T_right = 3 (handle_right(J) - J)

Condiciones
-----------
G1: T_right es proporcional a T_left (misma dirección):
    T_right = k * T_left   para algún k > 0

C1: T_right = T_left (igual dirección y magnitud):
    T_right = T_left

Tarea del alumno
----------------
Completar la función:
    enforce_continuity_at_join(spline, mode)

para que, según mode:
- mode=1: imponer G1
- mode=2: imponer C1
(mode=0 no hace nada)

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Seleccionar "ContinuityControl" y cambiar:
   - mode: 0 (sin imponer), 1 (G1), 2 (C1)
3) Rotar/mover "TangentTarget" (Empty):
   - Su posición relativa a J define el vector "objetivo" para orientar la tangente.
4) Ejecutar el checker:
   - Si la función está implementada correctamente, PASS en G1/C1.

Notas
-----
- Este ejercicio introduce una práctica típica: construir handles a partir de vectores.
- En Blender, para imponer tangentes en el punto J:
    handle_right(J) = J + v
  donde v es un vector desde J hacia el handle.

Mini-diagrama ASCII
-------------------
           (tramo 1)            (tramo 2)
P0 -------> J -----------------> P3
           ^ handle_left        ^ handle_right

G1: mismas direcciones
C1: mismas direcciones y longitudes
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab06_6_4_ContinuityTest"

_HANDLER_KEY = "LAB06_6_4_CONTINUITY_TEST_DRAW_HANDLER"
_TIMER_KEY = "LAB06_6_4_CONTINUITY_TEST_TIMER_REGISTERED"

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
    "LAB06_6_4_CONTINUITY_TEST_DRAW_HANDLER",
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
# Utilidades tangentes
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

def rel_mag_diff(a: float, b: float) -> float:
    return abs(a - b) / max(EPS, 0.5 * (a + b))


# -----------------------------
# TODO DEL ALUMNO
# -----------------------------
def enforce_continuity_at_join(spline, mode: int, v_target: Vector) -> None:
    """
    mode:
      0 -> no imponer nada
      1 -> imponer G1 (misma dirección)
      2 -> imponer C1 (misma dirección y magnitud)

    v_target:
      vector desde J hacia un "objetivo" que fija la dirección deseada de la tangente.

    Reglas:
    - Se debe ajustar EXCLUSIVAMENTE handle_right del punto J (bp1.handle_right).
    - No modificar handle_left del punto J (se considera "dado").
    - Mantener handles en modo FREE.
    """

    bp1 = spline.bezier_points[1]

    if mode == 0:
        return

    # Tangente izquierda dada por el estado actual de handle_left
    T_left = tangent_left_at_join(spline)

    # Dirección deseada (si v_target es degenerado, usar dirección de T_left)
    if v_target.length > EPS:
        dir_desired = v_target.normalized()
    elif T_left.length > EPS:
        dir_desired = T_left.normalized()
    else:
        dir_desired = Vector((1.0, 0.0, 0.0))

    # --- TODO: completar lógica G1/C1 ---
    # Pista:
    # - T_right = 3 (handle_right - J)
    # - Si queremos que T_right tenga dirección dir_desired, basta con:
    #     handle_right = J + alpha * dir_desired
    #   donde alpha controla la magnitud.
    #
    # Para G1:
    #   elegir alpha usando la magnitud actual del lado derecho (o una constante razonable),
    #   pero asegurando dirección dir_desired.
    #
    # Para C1:
    #   elegir alpha para que |T_right| == |T_left|
    #   (recuerda que el factor 3 aparece en ambos, así que basta con igualar longitudes
    #    de los vectores (handle_right - J) y (J - handle_left)).
    #
    # Sustituye el "pass" por tu implementación.

    # >>> TU CÓDIGO AQUÍ <<<
    pass


# -----------------------------
# Crear escena
# -----------------------------
def ensure_control_empty(col) -> bpy.types.Object:
    ctrl = bpy.data.objects.new("ContinuityControl", None)
    ctrl.empty_display_type = "CUBE"
    ctrl.empty_display_size = 0.25
    ctrl.location = Vector((0.0, -3.0, 0.0))
    col.objects.link(ctrl)

    ctrl["mode"] = 0  # 0,1,2
    return ctrl

def ensure_target_empty(col, join_pos: Vector) -> bpy.types.Object:
    tgt = bpy.data.objects.new("TangentTarget", None)
    tgt.empty_display_type = "ARROWS"
    tgt.empty_display_size = 0.5
    tgt.location = join_pos + Vector((1.0, 1.0, 0.0))
    col.objects.link(tgt)
    return tgt

def create_bezier_setup() -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name="SplineContinuityTest_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 24

    spline = curve_data.splines.new(type="BEZIER")
    spline.bezier_points.add(2)  # 3 puntos

    P0 = Vector((0.0, 0.0, 0.0))
    J  = Vector((2.0, 0.0, 0.0))
    P3 = Vector((4.0, 1.5, 0.0))

    bp0 = spline.bezier_points[0]
    bp1 = spline.bezier_points[1]
    bp2 = spline.bezier_points[2]

    for bp in (bp0, bp1, bp2):
        bp.handle_left_type = "FREE"
        bp.handle_right_type = "FREE"

    bp0.co = P0
    bp1.co = J
    bp2.co = P3

    # Estado inicial deliberadamente "incorrecto"
    bp0.handle_right = P0 + Vector((0.8, 1.2, 0.0))
    bp1.handle_left  = J  + Vector((-1.0, -0.6, 0.0))   # fija tangente izquierda
    bp1.handle_right = J  + Vector((0.6, 0.0, 0.0))     # se ajustará por el alumno
    bp2.handle_left  = P3 + Vector((-0.8, 0.0, 0.0))

    obj = bpy.data.objects.new("SplineContinuityTest", curve_data)
    return obj


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
    return {0: "0 (sin imponer)", 1: "1 (G1: dirección)", 2: "2 (C1: dirección+magnitud)"}.get(mode, "desconocido")

def _hud_draw_callback() -> None:
    x0, y0 = 20, 160
    line = 18

    _draw_text(x0, y0 + 6 * line, "Lab 06.6.4 — Test de continuidad: G1 y C1 (ajuste algorítmico)", size=16)
    _draw_text(x0, y0 + 5 * line, "Control: ContinuityControl['mode'] = 0,1,2; mover TangentTarget", size=13)

    ctrl = bpy.data.objects.get("ContinuityControl")
    obj = bpy.data.objects.get("SplineContinuityTest")
    tgt = bpy.data.objects.get("TangentTarget")
    if ctrl is None or obj is None or tgt is None or obj.type != "CURVE":
        _draw_text(x0, y0 + 4 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)
    rel = rel_mag_diff(TL.length, TR.length)

    _draw_text(x0, y0 + 4 * line, f"Modo: {mode_name(mode)}", size=13)
    _draw_text(x0, y0 + 3 * line, f"Ángulo tangentes (join): {ang:.3f} deg", size=13)
    _draw_text(x0, y0 + 2 * line, f"|T_left|={TL.length:.4f}  |T_right|={TR.length:.4f}", size=13)
    _draw_text(x0, y0 + 1 * line, f"Dif. relativa magnitudes: {rel:.4f}", size=13)
    _draw_text(x0, y0 + 0 * line, "G1: ángulo pequeño. C1: ángulo pequeño y magnitudes similares.", size=13)


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
# Timer: aplica la función del alumno (si mode>0)
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
    obj = bpy.data.objects.get("SplineContinuityTest")
    tgt = bpy.data.objects.get("TangentTarget")
    if ctrl is None or obj is None or tgt is None or obj.type != "CURVE":
        return 0.2

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    bp1 = spline.bezier_points[1]
    v_target = (tgt.location - bp1.co)

    # Llamada a la función del alumno
    enforce_continuity_at_join(spline, mode, v_target)

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

    curve_obj = create_bezier_setup()
    bpy.context.scene.collection.objects.link(curve_obj)
    move_object_to_collection_only(curve_obj, col)

    spline = curve_obj.data.splines[0]
    join_pos = spline.bezier_points[1].co.copy()

    ctrl = ensure_control_empty(col)
    tgt = ensure_target_empty(col, join_pos)

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    bpy.ops.object.select_all(action="DESELECT")
    ctrl.select_set(True)
    bpy.context.view_layer.objects.active = ctrl

    print("=== Lab 06.6.4 — Test de continuidad (plantilla alumno) ===")
    print("La escena previa ha sido eliminada.")
    print("Objetos: SplineContinuityTest, ContinuityControl, TangentTarget")
    print("Tarea: implementar enforce_continuity_at_join(spline, mode, v_target) para G1/C1.")

if __name__ == "__main__":
    main()


































































































def enforce_continuity_at_join_solution(spline, mode: int, v_target: Vector) -> None:
    """
    mode:
      0 -> no imponer nada
      1 -> imponer G1 (misma dirección)
      2 -> imponer C1 (misma dirección y magnitud)

    v_target:
      vector desde J hacia un "objetivo" que fija la dirección deseada de la tangente.

    Reglas:
    - Se ajusta exclusivamente bp1.handle_right.
    - No se modifica bp1.handle_left.
    """

    bp1 = spline.bezier_points[1]

    if mode == 0:
        return

    # Tangente izquierda (dada)
    T_left = tangent_left_at_join(spline)

    # Dirección deseada
    if v_target.length > EPS:
        dir_desired = v_target.normalized()
    elif T_left.length > EPS:
        dir_desired = T_left.normalized()
    else:
        dir_desired = Vector((1.0, 0.0, 0.0))

    # Longitud "base" (en términos de handle offset, no de tangente)
    # Porque T = 3 * (handle_offset), el factor 3 se cancela al comparar longitudes.
    left_handle_offset_len = (bp1.co - bp1.handle_left).length
    right_handle_offset_len_current = (bp1.handle_right - bp1.co).length

    if mode == 1:
        # G1: misma dirección, magnitud libre (conservamos la magnitud actual derecha si es válida;
        # si no, usamos la del lado izquierdo como valor razonable).
        alpha = right_handle_offset_len_current if right_handle_offset_len_current > EPS else max(EPS, left_handle_offset_len)
        bp1.handle_right = bp1.co + alpha * dir_desired
        return

    if mode == 2:
        # C1: misma dirección y magnitud -> igualar longitudes de offsets de handles
        alpha = max(EPS, left_handle_offset_len)
        bp1.handle_right = bp1.co + alpha * dir_desired
        return








































































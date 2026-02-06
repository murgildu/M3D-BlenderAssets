"""
Lab 04.4.1–04.4.2 — Tangente y recta tangente sobre una curva paramétrica (hélice)
=================================================================================

Objetivo
--------
Para una curva paramétrica P(u), u ∈ [0,1], visualizar:

(4.1) Tangente como derivada (numérica):
    P'(u0) ≈ (P(u0 + h) - P(u0 - h)) / (2h)

(4.2) Recta tangente en u0:
    Q(t) = P(u0) + t P'(u0),  t ∈ R

Aclaración de símbolos (u0 y t)
-------------------------------
- u0: valor concreto del parámetro u donde evaluamos la curva (un "punto" de la curva).
- t: parámetro independiente que recorre la recta tangente (no es el mismo que u).

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Seleccionar el objeto "TangentControl".
3) En Object Properties -> Custom Properties:
   - Ajustar u0 en [0,1] para desplazar el punto sobre la curva.
   - Ajustar t_span para la longitud de la recta tangente dibujada.
4) El viewport muestra:
   - Hélice (Curve)
   - Punto P(u0) (Empty)
   - Flecha tangente (Empty + geometría)
   - Segmento recta tangente (Curve POLY)

IMPORTANTE (visualización)
-------------------------
- El ejercicio usa objetos y geometría simple; no depende de materiales.
- La tangente se calcula numéricamente con paso h (editable en el script).

Mini-diagrama ASCII
-------------------
Curva: P(u)
           .
        .      <- P(u0)
      .  \      tangente P'(u0)
    .     \----->

Recta tangente: Q(t) = P(u0) + t P'(u0)
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab04_TangentHelix"

# -----------------------------
# Parámetros de la hélice
# (misma formulación que 03.3.4)
# -----------------------------
a = 1.5
turns = 4.0
b = 3.0
N_SAMPLES_CURVE = 220

# Paso derivada numérica (h)
H = 1e-3

# Flecha tangente (actualizable)
ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
UNIT_ARROW_HEAD_FRAC = 0.25

# HUD / timer
_HANDLER_KEY = "LAB04_TANGENT_DRAW_HANDLER"
_TIMER_KEY = "LAB04_TANGENT_TIMER_REGISTERED"

KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
    "LAB02_2_3_LAMBERT_DRAW_HANDLER",
    "LAB02_2_4_THRESHOLD_DRAW_HANDLER",
    "LAB03_3_4_PARAMETRIC_HELIX_DRAW_HANDLER",  # por si en el futuro existiera
    "LAB04_TANGENT_DRAW_HANDLER",
]

EPS_NONZERO = 1e-12


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
# Curva paramétrica (hélice)
# -----------------------------
def P(u: float) -> Vector:
    ang = 2.0 * math.pi * turns * u
    x = a * math.cos(ang)
    y = a * math.sin(ang)
    z = b * u
    return Vector((x, y, z))

def dP_numeric(u0: float, h: float) -> Vector:
    # central difference
    u_plus = min(1.0, u0 + h)
    u_minus = max(0.0, u0 - h)
    denom = (u_plus - u_minus)
    if denom < EPS_NONZERO:
        return Vector((0.0, 0.0, 0.0))
    return (P(u_plus) - P(u_minus)) / denom


# -----------------------------
# Construcción de la hélice como Curve (POLY)
# -----------------------------
def sample_points(n: int) -> list[Vector]:
    if n < 2:
        raise ValueError("N_SAMPLES_CURVE debe ser >= 2")
    pts = []
    for i in range(n):
        u = i / (n - 1)
        pts.append(P(u))
    return pts

def create_helix_curve_object(points: list[Vector], name: str = "HelixCurve") -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=name + "_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 12

    spline = curve_data.splines.new(type="POLY")
    spline.points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.points[i].co = (p.x, p.y, p.z, 1.0)

    # fino: sin bevel por defecto (puedes activar si quieres)
    curve_data.bevel_depth = 0.0

    obj = bpy.data.objects.new(name, curve_data)
    return obj


# -----------------------------
# Flecha actualizable (root + shaft + head)
# -----------------------------
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
    if direction.length < EPS_NONZERO:
        return
    d = direction.normalized()
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = z_axis.rotation_difference(d)

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

def update_arrow(arrow: dict, start: Vector, vec: Vector, desired_length: float = 1.0) -> None:
    """
    Dibuja una flecha desde start en dirección vec.
    desired_length controla la longitud visual (independiente de |vec|).
    """
    root, shaft, head = arrow["root"], arrow["shaft"], arrow["head"]
    root.location = start

    if vec.length < EPS_NONZERO:
        shaft.scale = Vector((1.0, 1.0, 0.0001))
        head.scale = Vector((1.0, 1.0, 0.0001))
        shaft.location = Vector((0.0, 0.0, 0.0))
        head.location = Vector((0.0, 0.0, 0.0))
        return

    orient_object_from_z_axis(root, vec)

    L = float(max(0.001, desired_length))
    head_len = max(0.05, min(L * UNIT_ARROW_HEAD_FRAC, 0.4))
    shaft_len = max(0.001, L - head_len)

    shaft.scale = Vector((1.0, 1.0, shaft_len))
    head.scale = Vector((1.0, 1.0, head_len))
    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))


# -----------------------------
# Recta tangente como Curve (POLY) con dos puntos: Q(-t_span) y Q(+t_span)
# -----------------------------
def ensure_tangent_line_object(name: str = "TangentLine") -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=name + "_Data", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 1

    spline = curve_data.splines.new(type="POLY")
    spline.points.add(1)  # 2 puntos
    spline.points[0].co = (0.0, 0.0, 0.0, 1.0)
    spline.points[1].co = (1.0, 0.0, 0.0, 1.0)

    obj = bpy.data.objects.new(name, curve_data)
    return obj

def update_tangent_line(obj: bpy.types.Object, p0: Vector, tangent: Vector, t_span: float) -> None:
    curve = obj.data
    spline = curve.splines[0]

    if tangent.length < EPS_NONZERO:
        q0 = p0
        q1 = p0
    else:
        tdir = tangent.normalized()
        q0 = p0 - t_span * tdir
        q1 = p0 + t_span * tdir

    spline.points[0].co = (q0.x, q0.y, q0.z, 1.0)
    spline.points[1].co = (q1.x, q1.y, q1.z, 1.0)


# -----------------------------
# Control (custom properties)
# -----------------------------
def ensure_control_empty(col) -> bpy.types.Object:
    ctrl = bpy.data.objects.new("TangentControl", None)
    ctrl.empty_display_type = "CUBE"
    ctrl.empty_display_size = 0.25
    ctrl.location = Vector((0.0, -3.0, 0.0))
    col.objects.link(ctrl)

    # Custom properties
    ctrl["u0"] = 0.25
    ctrl["t_span"] = 1.5
    ctrl["tan_len"] = 1.0  # longitud visual de la flecha tangente

    return ctrl


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
    x0, y0 = 20, 160
    line = 18

    _draw_text(x0, y0 + 6 * line, "Lab 04 — Tangente y recta tangente sobre hélice", size=16)
    _draw_text(x0, y0 + 5 * line, "Control: seleccionar 'TangentControl' y ajustar u0 / t_span", size=13)

    ctrl = bpy.data.objects.get("TangentControl")
    p_obj = bpy.data.objects.get("P_u0")
    if ctrl is None or p_obj is None:
        _draw_text(x0, y0 + 4 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    u0 = float(ctrl.get("u0", 0.25))
    u0 = max(0.0, min(1.0, u0))
    p0 = Vector(p_obj.location)

    t = dP_numeric(u0, H)
    t_len = t.length

    _draw_text(x0, y0 + 4 * line, f"u0 = {u0:.4f}   h = {H:.1e}", size=13)
    _draw_text(x0, y0 + 3 * line, f"P(u0) = ({p0.x:.3f}, {p0.y:.3f}, {p0.z:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"P'(u0) ≈ ({t.x:.3f}, {t.y:.3f}, {t.z:.3f})", size=13)
    _draw_text(x0, y0 + 1 * line, f"|P'(u0)| = {t_len:.4f}", size=13)
    _draw_text(x0, y0 + 0 * line, "Recta tangente: Q(t) = P(u0) + t P'(u0)  (t es parámetro de la recta)", size=13)

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
# Timer: actualización en tiempo real
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
    ctrl = bpy.data.objects.get("TangentControl")
    p_empty = bpy.data.objects.get("P_u0")
    arrow = bpy.app.driver_namespace.get("LAB04_ARROW_TANGENT")
    line_obj = bpy.data.objects.get("TangentLine")

    if any(x is None for x in (ctrl, p_empty, arrow, line_obj)):
        return 0.1

    u0 = float(ctrl.get("u0", 0.25))
    u0 = max(0.0, min(1.0, u0))

    t_span = float(ctrl.get("t_span", 1.5))
    t_span = max(0.01, t_span)

    tan_len = float(ctrl.get("tan_len", 1.0))
    tan_len = max(0.01, tan_len)

    p0 = P(u0)
    p_empty.location = p0

    t = dP_numeric(u0, H)

    update_arrow(arrow, p0, t, desired_length=tan_len)
    update_tangent_line(line_obj, p0, t, t_span)

    _tag_redraw_all_3dviews()
    return 0.05


# -----------------------------
# Escena
# -----------------------------
def create_scene_demo() -> None:
    col = ensure_collection(LAB_COLLECTION_NAME)

    # Hélice
    pts = sample_points(N_SAMPLES_CURVE)
    helix = create_helix_curve_object(pts, "HelixCurve")
    bpy.context.scene.collection.objects.link(helix)
    move_object_to_collection_only(helix, col)

    # Control
    ctrl = ensure_control_empty(col)
    move_object_to_collection_only(ctrl, col)

    # Punto P(u0)
    p_empty = bpy.data.objects.new("P_u0", None)
    p_empty.empty_display_type = "SPHERE"
    p_empty.empty_display_size = 0.18
    p_empty.location = P(float(ctrl["u0"]))
    col.objects.link(p_empty)
    move_object_to_collection_only(p_empty, col)

    # Flecha tangente
    arrow = create_unit_arrow(col, "TangentArrow", p_empty.location)
    bpy.app.driver_namespace["LAB04_ARROW_TANGENT"] = arrow

    # Recta tangente
    tline = ensure_tangent_line_object("TangentLine")
    bpy.context.scene.collection.objects.link(tline)
    move_object_to_collection_only(tline, col)

    # Selección: control activo
    bpy.ops.object.select_all(action="DESELECT")
    ctrl.select_set(True)
    bpy.context.view_layer.objects.active = ctrl


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    _unregister_timer_if_needed()
    wipe_scene()
    create_scene_demo()

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    print("=== Lab 04 — Tangente y recta tangente (hélice) ===")
    print("La escena previa ha sido eliminada.")
    print("Control: seleccionar 'TangentControl' -> Custom Properties: u0, t_span, tan_len")
    print("Se actualizan: P(u0), flecha tangente y recta tangente.")


if __name__ == "__main__":
    main()


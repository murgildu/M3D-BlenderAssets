"""
Lab 01.1.3 — Norma (módulo) y normalización (con HUD en viewport)
=================================================================

Modelo teórico
--------------
- Norma (módulo): |v| = sqrt(v · v)
- Normalización (si |v| != 0): v_hat = v / |v|
- Propiedad: |v_hat| = 1

Objetivo práctico (evaluación)
------------------------------
El alumno debe construir manualmente el vector unitario (módulo 1) en la misma
dirección que v:

1) Mover "V_tip_user" para definir el vector v (desde O):
      v = V_tip_user - O
2) Mover "V_hat_tip_user" para que coincida con "V_hat_target".
   (V_hat_target = O + v_hat, calculado por el script)

El HUD evalúa:
- error_dir = dist(V_hat_tip_user, V_hat_target)
- error_unit = abs( dist(O, V_hat_tip_user) - 1 )

Mini-diagrama ASCII
-------------------
          V_tip_user
              o
             /
            /   v
           /
O --------o--------------------->  (dirección de v)

O --------o----->  V_hat_target  (vector unitario objetivo)
          \
           o V_hat_tip_user      (vector unitario propuesto por el alumno)

Nota (HUD persistente)
----------------------
Los HUDs se implementan con draw handlers y pueden persistir durante la sesión de Blender.
Este script elimina HUDs previos conocidos antes de instalar el suyo.
"""

import bpy
import blf
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab01_1_3_NormNormalize"

# Configuración
ORIGIN = Vector((0.0, 0.0, 0.0))
V_INIT = Vector((2.0, 1.0, 0.5))

# Geometría de flechas (base de longitud 1.0, luego se escala)
ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
UNIT_ARROW_HEAD_FRAC = 0.25  # fracción de la longitud total dedicada a la "punta" (aprox)

# Tolerancias
EPS_DIR = 0.05      # tolerancia para coincidir con V_hat_target (5 cm)
EPS_UNIT = 0.05     # tolerancia para módulo 1 (5 cm)
EPS_NONZERO = 1e-6  # para evitar normalizar el vector nulo

# HUD handlers
_HANDLER_KEY = "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER"
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
]

# Timer
_TIMER_KEY = "LAB01_1_3_TIMER_REGISTERED"


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
# Limpieza total de la escena
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
# Flecha actualizable (root + shaft + head)
# -----------------------------
def create_unit_arrow(col, base_name: str, start: Vector) -> dict:
    """
    Crea una flecha de longitud 1 en +Z en coordenadas locales, con:
    - root (Empty)
    - shaft (cylinder depth=1)
    - head (cone depth=1)
    Luego se actualizará con update_arrow(...) para cualquier vector.
    """
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

    # Colocación inicial (para longitud 1):
    # shaft ocupa [0, 1-head] y head ocupa [1-head, 1]
    # (en local Z)
    return {"root": root, "shaft": shaft, "head": head}


def update_arrow(arrow: dict, start: Vector, vec: Vector) -> None:
    """
    Ajusta la flecha para representar 'vec' desde 'start':
    - posiciona el root en start
    - orienta el root a la dirección de vec
    - ajusta la longitud escalando y recolocando shaft/head (sin recrear mallas)
    """
    root = arrow["root"]
    shaft = arrow["shaft"]
    head = arrow["head"]

    root.location = start

    L = vec.length
    if L < 1e-9:
        # Si es vector nulo: colapsar y no orientar
        shaft.scale = Vector((1.0, 1.0, 0.0001))
        head.scale = Vector((1.0, 1.0, 0.0001))
        shaft.location = Vector((0.0, 0.0, 0.0))
        head.location = Vector((0.0, 0.0, 0.0))
        return

    orient_object_from_z_axis(root, vec)

    head_len = max(0.05, min(L * UNIT_ARROW_HEAD_FRAC, 0.4))  # limitar visualmente
    shaft_len = max(0.001, L - head_len)

    # Como las mallas tienen depth=1, escalamos en Z a la longitud deseada
    shaft.scale = Vector((1.0, 1.0, shaft_len))
    head.scale = Vector((1.0, 1.0, head_len))

    # Recolocar centros:
    # cilindro: centrado en shaft_len/2
    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    # cono: centrado en shaft_len + head_len/2
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))


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
    x0, y0 = 20, 110
    line = 18

    _draw_text(x0, y0 + 5 * line, "Lab 01.1.3 — Norma y normalización", size=16)
    _draw_text(x0, y0 + 4 * line, "Acción: mover 'V_tip_user' y ajustar 'V_hat_tip_user' hasta 'V_hat_target'", size=13)

    O = bpy.data.objects.get("O")
    V_tip_user = bpy.data.objects.get("V_tip_user")
    V_hat_tip_user = bpy.data.objects.get("V_hat_tip_user")
    V_hat_target = bpy.data.objects.get("V_hat_target")

    if any(o is None for o in (O, V_tip_user, V_hat_tip_user, V_hat_target)):
        _draw_text(x0, y0 + 3 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    o = Vector(O.location)
    v = Vector(V_tip_user.location) - o
    v_len = v.length

    _draw_text(x0, y0 + 3 * line, f"v = V_tip_user - O = ({v.x:.3f}, {v.y:.3f}, {v.z:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"|v| = {v_len:.4f}", size=13)

    if v_len < EPS_NONZERO:
        _draw_text(x0, y0 + 1 * line, "Normalización: no definida (|v| ~ 0). Mover V_tip_user.", size=13)
        return

    # Evaluación del alumno
    err_dir = (Vector(V_hat_tip_user.location) - Vector(V_hat_target.location)).length
    d_user = (Vector(V_hat_tip_user.location) - o).length
    err_unit = abs(d_user - 1.0)

    ok = (err_dir < EPS_DIR) and (err_unit < EPS_UNIT)
    status = "PASS" if ok else "FAIL"

    _draw_text(x0, y0 + 1 * line, f"error_dir = dist(V_hat_tip_user, V_hat_target) = {err_dir:.4f}   (EPS_DIR={EPS_DIR:.3f})", size=13)
    _draw_text(x0, y0 + 0 * line, f"error_unit = abs(dist(O, V_hat_tip_user) - 1) = {err_unit:.4f}   (EPS_UNIT={EPS_UNIT:.3f})   {status}", size=13)


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
# Timer de actualización (flechas + target)
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
    V_tip_user = bpy.data.objects.get("V_tip_user")
    V_hat_target = bpy.data.objects.get("V_hat_target")

    if any(x is None for x in (O, V_tip_user, V_hat_target)):
        return 0.1

    o = Vector(O.location)
    v = Vector(V_tip_user.location) - o
    if v.length < EPS_NONZERO:
        # Colapsar target al origen si no hay dirección
        V_hat_target.location = o
    else:
        v_hat = v.normalized()
        V_hat_target.location = o + v_hat

    # Actualizar flechas si existen
    arrow_v = bpy.app.driver_namespace.get("LAB01_1_3_ARROW_V")
    arrow_vhat = bpy.app.driver_namespace.get("LAB01_1_3_ARROW_VHAT")
    if arrow_v is not None:
        update_arrow(arrow_v, o, v)
    if arrow_vhat is not None:
        if v.length < EPS_NONZERO:
            update_arrow(arrow_vhat, o, Vector((0, 0, 0)))
        else:
            update_arrow(arrow_vhat, o, v.normalized())

    _tag_redraw_all_3dviews()
    return 0.05  # ~20 fps


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    _unregister_timer_if_needed()
    wipe_scene()

    col = ensure_collection(LAB_COLLECTION_NAME)

    # Guardar tolerancias en escena para el checker
    bpy.context.scene["LAB01_1_3_EPS_DIR"] = float(EPS_DIR)
    bpy.context.scene["LAB01_1_3_EPS_UNIT"] = float(EPS_UNIT)

    # Crear puntos
    create_empty_in_collection(col, "O", ORIGIN, display="ARROWS", size=0.25)
    create_empty_in_collection(col, "V_tip_user", V_INIT, display="SPHERE", size=0.28)

    # Punto objetivo y punto del alumno para el vector normalizado
    v_hat_init = V_INIT.normalized()
    create_empty_in_collection(col, "V_hat_target", ORIGIN + v_hat_init, display="CUBE", size=0.22)

    # Inicialmente, colocar el tip del alumno en una posición desplazada (para que no empiece en PASS)
    create_empty_in_collection(col, "V_hat_tip_user", ORIGIN + v_hat_init + Vector((0.35, -0.25, 0.15)), display="SPHERE", size=0.28)

    # Crear flechas actualizables y guardarlas en driver_namespace
    arrow_v = create_unit_arrow(col, "v_arrow", ORIGIN)
    arrow_vhat = create_unit_arrow(col, "v_hat_arrow", ORIGIN)
    bpy.app.driver_namespace["LAB01_1_3_ARROW_V"] = arrow_v
    bpy.app.driver_namespace["LAB01_1_3_ARROW_VHAT"] = arrow_vhat

    # Inicializar flechas con el estado inicial
    update_arrow(arrow_v, ORIGIN, V_INIT)
    update_arrow(arrow_vhat, ORIGIN, v_hat_init)

    # Instalar HUD y timer
    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    print("=== Lab 01.1.3 — Norma y normalización ===")
    print("La escena previa ha sido eliminada.")
    print("Acción: mover 'V_tip_user' para definir v y ajustar 'V_hat_tip_user' hasta 'V_hat_target'.")
    print("El HUD muestra error_dir y error_unit (PASS cuando ambos están dentro de tolerancia).")
    print("Colección creada:", LAB_COLLECTION_NAME)


if __name__ == "__main__":
    main()


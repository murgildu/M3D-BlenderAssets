import bpy
from mathutils import Vector
import math

EPS_NONZERO = 1e-6

def get_obj(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"No se encontró el objeto requerido: '{name}'")
    return obj

def main() -> None:
    O = get_obj("O")
    U_tip = get_obj("U_tip")
    V_tip_user = get_obj("V_tip_user")
    V_tip_target = get_obj("V_tip_target")

    eps_pos = float(bpy.context.scene.get("LAB02_2_2_EPS_POS", 0.05))
    eps_dot = float(bpy.context.scene.get("LAB02_2_2_EPS_DOT", 0.05))

    o = Vector(O.location)
    u = Vector(U_tip.location) - o
    v_user = Vector(V_tip_user.location) - o

    # restringir a XY
    u2 = Vector((u.x, u.y, 0.0))
    v2 = Vector((v_user.x, v_user.y, 0.0))

    if u2.length < EPS_NONZERO or v2.length < EPS_NONZERO:
        print("=== Checker Lab 02.2.2 — Ortogonalidad (2D) ===")
        print("RESULTADO: FAIL (vector nulo).")
        print("Asegúrate de que u y v_user no sean nulos.")
        return

    dot = u2.dot(v2)

    # error posicional respecto al target
    err_pos = (Vector(V_tip_user.location) - Vector(V_tip_target.location)).length

    # tolerancia dot proporcional al tamaño (misma condición que HUD)
    ok_dot = abs(dot) < eps_dot * u2.length * v2.length
    ok_pos = err_pos < eps_pos

    # Ángulo para reporte
    dot_n = max(-1.0, min(1.0, u2.normalized().dot(v2.normalized())))
    ang_deg = math.degrees(math.acos(dot_n))

    print("=== Checker Lab 02.2.2 — Ortogonalidad (2D) ===")
    print(f"u·v_user = {dot:.6f}")
    print(f"angle(u,v_user) = {ang_deg:.3f} deg")
    print(f"error_pos = {err_pos:.6f}   (EPS_POS={eps_pos})")
    print(f"cond_dot  = {ok_dot}   (EPS_DOT={eps_dot} proporcional)")
    print(f"cond_pos  = {ok_pos}")

    if ok_dot and ok_pos:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        if not ok_pos:
            print(" - Ajuste: acerca V_tip_user a V_tip_target.")
        if not ok_dot:
            print(" - Ortogonalidad: u·v_user no es suficientemente cercano a 0.")

if __name__ == "__main__":
    main()


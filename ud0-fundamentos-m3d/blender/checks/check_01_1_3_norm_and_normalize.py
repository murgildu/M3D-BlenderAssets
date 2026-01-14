"""
Checker Lab 01.1.3 — Norma y normalización
==========================================

Valida que el alumno ha colocado V_hat_tip_user de modo que:
- esté cerca de V_hat_target (dirección correcta)
- esté a distancia ~ 1 del origen O (módulo unitario)

Si v ~ 0, el ejercicio no es evaluable (no hay dirección para normalizar).
"""

import bpy
from mathutils import Vector

EPS_NONZERO = 1e-6


def get_obj(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"No se encontró el objeto requerido: '{name}'")
    return obj


def main() -> None:
    O = get_obj("O")
    V_tip_user = get_obj("V_tip_user")
    V_hat_target = get_obj("V_hat_target")
    V_hat_tip_user = get_obj("V_hat_tip_user")

    eps_dir = float(bpy.context.scene.get("LAB01_1_3_EPS_DIR", 0.05))
    eps_unit = float(bpy.context.scene.get("LAB01_1_3_EPS_UNIT", 0.05))

    o = Vector(O.location)
    v = Vector(V_tip_user.location) - o
    v_len = v.length

    print("=== Checker Lab 01.1.3 — Norma y normalización ===")
    print(f"|v| = {v_len:.6f}")

    if v_len < EPS_NONZERO:
        print("RESULTADO: FAIL")
        print("Motivo: |v| ~ 0 (normalización indefinida). Mueve V_tip_user para que v sea no nulo.")
        return

    err_dir = (Vector(V_hat_tip_user.location) - Vector(V_hat_target.location)).length
    d_user = (Vector(V_hat_tip_user.location) - o).length
    err_unit = abs(d_user - 1.0)

    print(f"error_dir  = {err_dir:.6f}   (EPS_DIR={eps_dir})")
    print(f"dist_user  = {d_user:.6f}   -> error_unit = {err_unit:.6f}   (EPS_UNIT={eps_unit})")

    ok = (err_dir < eps_dir) and (err_unit < eps_unit)

    if ok:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        if err_dir >= eps_dir:
            print(" - Dirección: acerca V_hat_tip_user a V_hat_target.")
        if err_unit >= eps_unit:
            print(" - Módulo: ajusta V_hat_tip_user para que dist(O, V_hat_tip_user) sea aproximadamente 1.")


if __name__ == "__main__":
    main()


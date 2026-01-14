"""
Checker Lab 01.1.1 — Traslación
===============================

Valida que P_user se ha colocado en P_target dentro de la tolerancia EPS.
"""

import bpy
from mathutils import Vector

EPS = 0.02


def get_obj(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"No se encontró el objeto requerido: '{name}'")
    return obj


def main() -> None:
    P_user = get_obj("P_user")
    P_target = get_obj("P_target")

    err = (Vector(P_user.location) - Vector(P_target.location)).length

    print("=== Checker Lab 01.1.1 — Traslación ===")
    print(f"P_user.location   = {tuple(P_user.location)}")
    print(f"P_target.location = {tuple(P_target.location)}")
    print(f"Error |P_user - P_target| = {err:.6f}")
    print(f"EPS = {EPS}")

    if err < EPS:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Sugerencia: selecciona 'P_user', pulsa G y ajústalo hasta coincidir con 'P_target'.")


if __name__ == "__main__":
    main()


import bpy
from mathutils import Vector

EPS_POS = 0.03
EPS_RATIO = 0.05


def get_obj(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"No se encontró el objeto requerido: '{name}'")
    return obj


def main() -> None:
    C = get_obj("C_pivot")
    P = get_obj("P")
    P_user = get_obj("P_user")
    P_target = get_obj("P_target")

    k = float(bpy.context.scene.get("LAB01_1_2_K", 1.8))

    C_loc = Vector(C.location)
    P_loc = Vector(P.location)
    U_loc = Vector(P_user.location)
    T_loc = Vector(P_target.location)

    err_pos = (U_loc - T_loc).length

    d0 = (P_loc - C_loc).length
    d1 = (U_loc - C_loc).length
    ratio = (d1 / d0) if d0 > 1e-9 else float("inf")

    print("=== Checker Lab 01.1.2 — Escalado respecto a pivote ===")
    print(f"k (scene)         = {k}")
    print(f"Error posicional  = {err_pos:.6f}   (EPS_POS={EPS_POS})")
    print(f"Ratio d1/d0       = {ratio:.6f}   (EPS_RATIO={EPS_RATIO})")

    ok_pos = err_pos < EPS_POS
    ok_ratio = abs(ratio - k) < EPS_RATIO

    if ok_pos and ok_ratio:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        if not ok_pos:
            print(" - Ajuste: acerca 'P_user' a 'P_target' (tecla G).")
        if not ok_ratio:
            print(" - Escalado: revisa la distancia radial al pivote (desde C_pivot).")


if __name__ == "__main__":
    main()


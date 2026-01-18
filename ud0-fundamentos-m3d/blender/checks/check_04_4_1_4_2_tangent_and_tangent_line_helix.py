import bpy
from mathutils import Vector
import math

# mismos parámetros que el script (deben mantenerse consistentes)
a = 1.5
turns = 4.0
b = 3.0
H = 1e-3
EPS_NONZERO = 1e-12

def P(u: float) -> Vector:
    ang = 2.0 * math.pi * turns * u
    return Vector((a * math.cos(ang), a * math.sin(ang), b * u))

def dP_numeric(u0: float, h: float) -> Vector:
    u_plus = min(1.0, u0 + h)
    u_minus = max(0.0, u0 - h)
    denom = (u_plus - u_minus)
    if denom < EPS_NONZERO:
        return Vector((0.0, 0.0, 0.0))
    return (P(u_plus) - P(u_minus)) / denom

def main() -> None:
    ctrl = bpy.data.objects.get("TangentControl")
    p = bpy.data.objects.get("P_u0")
    line_obj = bpy.data.objects.get("TangentLine")
    if any(x is None for x in (ctrl, p, line_obj)):
        raise RuntimeError("Faltan objetos del lab. Ejecuta primero el script de Lab 04.")

    u0 = float(ctrl.get("u0", 0.25))
    u0 = max(0.0, min(1.0, u0))

    p0 = P(u0)
    t = dP_numeric(u0, H)

    print("=== Checker Lab 04 — Tangente y recta tangente ===")
    print(f"u0 = {u0:.6f}")
    print(f"P(u0) = {tuple(p0)}")
    print(f"P'(u0) ≈ {tuple(t)}")
    print(f"|P'(u0)| = {t.length:.6f}")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()


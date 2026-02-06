import bpy
from mathutils import Vector
import math

EPS = 1e-12

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

def main() -> None:
    ctrl = bpy.data.objects.get("ContinuityControl")
    obj = bpy.data.objects.get("SplineContinuity")
    if ctrl is None or obj is None or obj.type != "CURVE":
        raise RuntimeError("Faltan objetos del lab 06.6.1. Ejecuta primero el script correspondiente.")

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)
    lenL = TL.length
    lenR = TR.length
    rel = abs(lenL - lenR) / max(EPS, (0.5 * (lenL + lenR)))

    print("=== Checker Lab 06.6.1 — Continuidad C0/G1/C1 ===")
    print(f"mode = {mode}")
    print(f"angle(T_left, T_right) = {ang:.6f} deg")
    print(f"|T_left| = {lenL:.6f}, |T_right| = {lenR:.6f}")
    print(f"rel_diff = {rel:.6f}")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()


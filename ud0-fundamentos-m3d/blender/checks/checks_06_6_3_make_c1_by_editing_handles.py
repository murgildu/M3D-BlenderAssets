import bpy
from mathutils import Vector
import math

ANGLE_EPS_DEG = 3.0
MAG_REL_EPS = 0.08   # 8% (ajustable; razonable para "aproximar" C1)

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

def rel_mag_diff(a: float, b: float) -> float:
    return abs(a - b) / max(EPS, 0.5 * (a + b))

def main() -> None:
    obj = bpy.data.objects.get("SplineC1Task")
    if obj is None or obj.type != "CURVE":
        raise RuntimeError("No se encontró 'SplineC1Task'. Ejecuta primero el lab 06.6.3.")

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)
    lenL = TL.length
    lenR = TR.length
    rel = rel_mag_diff(lenL, lenR)

    print("=== Checker Lab 06.6.3 — C1 por edición de handles ===")
    print(f"angle(T_left, T_right) = {ang:.6f} deg   (umbral {ANGLE_EPS_DEG:.3f})")
    print(f"|T_left| = {lenL:.6f}  |T_right| = {lenR:.6f}")
    print(f"rel_diff_magnitude = {rel:.6f}  (umbral {MAG_REL_EPS:.3f})")

    ok_angle = ang < ANGLE_EPS_DEG
    ok_mag = rel < MAG_REL_EPS

    if ok_angle and ok_mag:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        if not ok_angle:
            print("- Ajuste necesario: alinear handles (dirección).")
        if not ok_mag:
            print("- Ajuste necesario: igualar longitudes de handles en el punto central (simetría).")

if __name__ == "__main__":
    main()


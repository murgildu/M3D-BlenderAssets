import bpy

def main() -> None:
    required = ["ControlPolygon", "BezierFormula", "BezierBlender", "Tangent0", "Tangent1"]
    for name in required:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"Falta el objeto '{name}'. Ejecuta primero el lab 05.5.2–05.5.3.")

    formula = bpy.data.objects.get("BezierFormula")
    if formula.type != "MESH":
        raise RuntimeError("'BezierFormula' debe ser un mesh.")

    v = len(formula.data.vertices)
    e = len(formula.data.edges)

    print("=== Checker Lab 05.5.2–05.5.3 — Bézier por fórmula vs Blender ===")
    print(f"BezierFormula: vertices={v}, edges={e}")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()


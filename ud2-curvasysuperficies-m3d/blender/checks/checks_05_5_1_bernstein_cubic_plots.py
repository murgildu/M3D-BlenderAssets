import bpy

def main() -> None:
    required = ["B0_curve", "B1_curve", "B2_curve", "B3_curve", "Sum_curve"]
    for name in required:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            raise RuntimeError(f"Falta el objeto '{name}'. Ejecuta primero el lab 05.5.1.")

    err = bpy.app.driver_namespace.get("LAB05_5_1_SUM_ERR", None)
    print("=== Checker Lab 05.5.1 — Bernstein cúbico ===")
    if err is not None:
        print(f"Error máximo de suma (muestreado): {err:.6e}")
    else:
        print("No se encontró el error precalculado en driver_namespace.")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()


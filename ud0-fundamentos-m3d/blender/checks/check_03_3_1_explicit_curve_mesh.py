import bpy

def main() -> None:
    obj = bpy.data.objects.get("ExplicitCurve")
    if obj is None or obj.type != "MESH":
        raise RuntimeError("No se encontró el objeto mesh 'ExplicitCurve'. Ejecuta primero el script del lab 03.3.1.")

    mesh = obj.data
    v = len(mesh.vertices)
    e = len(mesh.edges)

    print("=== Checker Lab 03.3.1 — Curva explícita (mesh) ===")
    print(f"Vertices: {v}")
    print(f"Edges:    {e}")

    if v >= 2 and e == v - 1:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Condición esperada: edges = vertices - 1 y vertices >= 2.")

if __name__ == "__main__":
    main()


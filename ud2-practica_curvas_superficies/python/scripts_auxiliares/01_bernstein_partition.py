# -*- coding: utf-8 -*-

"""
01_bernstein_partition.py
========================

Objetivo
--------
1) Implementar los polinomios de Bernstein B_{i,n}(u).
2) Visualizar B0..Bn para n=3.
3) Verificar la propiedad de "partición de la unidad":
      sum_i B_{i,n}(u) = 1   para todo u en [0,1]

Dependencias
-----------
- math
- numpy
- matplotlib

Ejecución
---------
python 01_bernstein_partition.py

Qué extraer para Blender
------------------------
- bernstein(n, i, u)
- bernstein_all(n, u)
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def bernstein(n: int, i: int, u: float) -> float:
    """
    Polinomio de Bernstein:
        B_{i,n}(u) = C(n,i) * u^i * (1-u)^(n-i)

    Donde:
      - n es el grado total
      - i es el índice (0..n)
      - u está en [0,1]

    Propiedades importantes en [0,1]:
      - B_{i,n}(u) >= 0
      - sum_{i=0..n} B_{i,n}(u) = 1  (partición de la unidad)
    """
    if i < 0 or i > n:
        return 0.0
    return math.comb(n, i) * (u ** i) * ((1.0 - u) ** (n - i))


def bernstein_all(n: int, u: float):
    """Devuelve la lista [B_{0,n}(u), B_{1,n}(u), ..., B_{n,n}(u)]."""
    return [bernstein(n, i, u) for i in range(n + 1)]


def main():
    n = 3
    u = np.linspace(0.0, 1.0, 300)

    # Calculamos todos los Bernstein para cada u
    Bs = np.zeros((n + 1, len(u)))
    for k in range(n + 1):
        Bs[k, :] = [bernstein(n, k, ui) for ui in u]

    # Verificación de partición de unidad
    s = np.sum(Bs, axis=0)
    max_err = float(np.max(np.abs(s - 1.0)))
    print(f"[Bernstein] n={n} -> max |sum(B)-1| = {max_err:.6e}")

    # Dibujo
    plt.figure(figsize=(10, 5))
    for k in range(n + 1):
        plt.plot(u, Bs[k, :], lw=2, label=f"B{k},{n}(u)")
    plt.plot(u, s, "--", lw=2, label="Suma")

    plt.title(f"Polinomios de Bernstein (n={n}) y suma")
    plt.xlabel("u")
    plt.ylabel("valor")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()


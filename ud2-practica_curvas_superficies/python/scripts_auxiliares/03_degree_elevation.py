
# -*- coding: utf-8 -*-
"""
03_degree_elevation.py
======================

Objetivo
--------
Implementar elevación de grado (degree elevation) para una curva Bézier
SIN cambiar la geometría de la curva.

Si P define una Bézier de grado n (n+1 puntos),
la curva equivalente de grado n+1 tiene n+2 puntos Q:

  Q0     = P0
  Q_{n+1}= Pn
  Qi     = (i/(n+1)) P_{i-1} + (1 - i/(n+1)) P_i   para i=1..n

Dependencias
-----------
- numpy
- math
- matplotlib

Ejecución
---------
python 03_degree_elevation.py

Qué extraer para Blender
------------------------
- elevate_degree(P)
- max_curve_distance(P, Q)
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def bernstein(n: int, i: int, u: float) -> float:
    return math.comb(n, i) * (u ** i) * ((1.0 - u) ** (n - i))


def bezier_point(P: np.ndarray, u: float) -> np.ndarray:
    n = len(P) - 1
    out = np.zeros(P.shape[1], dtype=float)
    for i in range(n + 1):
        out += bernstein(n, i, u) * P[i]
    return out


def bezier_curve(P: np.ndarray, num_samples: int = 200) -> np.ndarray:
    u_values = np.linspace(0.0, 1.0, num_samples)
    return np.array([bezier_point(P, u) for u in u_values], dtype=float)


def elevate_degree(P: np.ndarray) -> np.ndarray:
    """
    Eleva el grado de Bézier sin cambiar la curva.

    P: (n+1, dim)
    Q: (n+2, dim)
    """
    n = len(P) - 1
    if n < 1:
        raise ValueError("Se necesita al menos una curva de grado 1")

    Q = np.zeros((n + 2, P.shape[1]), dtype=float)
    Q[0] = P[0]
    Q[n + 1] = P[n]

    # Fórmula estándar de elevación de grado
    for i in range(1, n + 1):
        alpha = i / (n + 1)
        Q[i] = alpha * P[i - 1] + (1.0 - alpha) * P[i]

    return Q


def max_curve_distance(P: np.ndarray, Q: np.ndarray, num_samples: int = 200) -> float:
    """
    Distancia máxima entre dos curvas muestreadas (mismos u).
    Ideal para verificar que la elevación "no cambia" la curva.
    """
    u_values = np.linspace(0.0, 1.0, num_samples)
    maxd = 0.0
    for u in u_values:
        a = bezier_point(P, u)
        b = bezier_point(Q, u)
        maxd = max(maxd, float(np.linalg.norm(a - b)))
    return maxd


def main():
    # Ejemplo: cuadrática (3 puntos) en 2D
    P = np.array([
        [0.0, 0.0],
        [3.0, 4.0],
        [6.0, 0.0]
    ], dtype=float)

    Q = elevate_degree(P)
    err = max_curve_distance(P, Q, 250)

    print("[Degree Elevation]")
    print("Original (grado 2):\n", P)
    print("Elevada  (grado 3):\n", np.round(Q, 6))
    print("max |P(u)-Q(u)| =", err)

    # Curvas para visualizar
    cP = bezier_curve(P, 250)
    cQ = bezier_curve(Q, 250)

    plt.figure(figsize=(9, 5))
    plt.plot(cP[:, 0], cP[:, 1], lw=2, label="Curva original (grado 2)")
    plt.plot(cQ[:, 0], cQ[:, 1], "--", lw=2, label="Curva elevada (grado 3)")
    plt.plot(P[:, 0], P[:, 1], "o-", label="Controles P")
    plt.plot(Q[:, 0], Q[:, 1], "o--", label="Controles Q")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.title("Elevación de grado: misma curva, más puntos de control")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

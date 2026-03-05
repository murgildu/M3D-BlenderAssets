import numpy as np
import matplotlib.pyplot as plt

def create_knot_vector(n, p):
    return np.array([0]*p + list(range(n - p + 2)) + [n - p + 1]*p, dtype=float)

def nurbs_curve(P, weights, p=3, num_samples=100):
    n = len(P) - 1
    t = create_knot_vector(n, p)
    u_steps = np.linspace(t[p], t[n+1], num_samples)
    
    curve_pts = []
    for x in u_steps:
        k = min(np.searchsorted(t, x, side='right') - 1, n)
        
        # Trabajamos en coordenadas homogéneas: (w*x, w*y, w)
        d = []
        for j in range(p + 1):
            idx = j + k - p
            pt = np.array(P[idx])
            w = weights[idx]
            d.append(np.append(pt * w, w)) # Guardamos [wx, wy, w]

        # Algoritmo de De Boor sobre las coordenadas homogéneas
        for r in range(1, p + 1):
            for j in range(p, r - 1, -1):
                alpha = (x - t[j + k - p]) / (t[j + k + 1 - r] - t[j + k - p])
                d[j] = (1.0 - alpha) * d[j - 1] + alpha * d[j]
        
        # Volvemos a 2D dividiendo por la última componente (w final)
        res = d[p]
        curve_pts.append(res[:-1] / res[-1])
        
    return np.array(curve_pts)

# --- Comparativa de Pesos ---
P = np.array([[0,0], [2,5], [5,5], [8,0]])
W_normal = [1, 1, 1, 1]      # B-Spline estándar
W_fuerte = [1, 10, 1, 1]     # El punto P1 atrae mucho más la curva

curva_1 = nurbs_curve(P, W_normal)
curva_2 = nurbs_curve(P, W_fuerte)

plt.plot(P[:,0], P[:,1], 'ro--', label="Polígono")
plt.plot(curva_1[:,0], curva_1[:,1], 'b-', label="Peso normal (w=1)")
plt.plot(curva_2[:,0], curva_2[:,1], 'g--', label="Peso alto en P1 (w=10)")
plt.legend()
plt.show()
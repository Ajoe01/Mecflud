# calculations/fluid.py

G_DEFAULT = 9.81
RHO_WATER = 1000.0       # kg/m3
NU_WATER = 1.0e-6        # m2/s (~20°C)

def hydrostatic_pressure(depth: float, rho: float = None, g: float = None) -> float:
    """p = rho * g * h (manométrica)."""
    if depth is None or depth < 0:
        raise ValueError("Profundidad inválida.")
    rho = rho if (rho and rho > 0) else RHO_WATER
    g = g if (g and g > 0) else G_DEFAULT
    return rho * g * depth

def reynolds(V: float, D: float, nu: float = None) -> tuple[float, str]:
    """Re = V D / nu. Devuelve (Re, régimen)."""
    if V is None or D is None or V <= 0 or D <= 0:
        raise ValueError("V y D deben ser > 0.")
    nu = nu if (nu and nu > 0) else NU_WATER
    Re = V * D / nu
    if Re < 2000:
        reg = "Laminar"
    elif Re <= 4000:
        reg = "Transicional"
    else:
        reg = "Turbulento"
    return Re, reg

def friction_factor(Re: float, rel_rough: float) -> float:
    """f de Darcy. Laminar: 64/Re. Turbulento: Haaland explícito."""
    if Re < 1e-9:
        raise ValueError("Reynolds inválido.")
    if Re < 2000.0:
        return 64.0 / Re
    # Haaland:
    # 1/sqrt(f) = -1.8 * log10( ( (ε/D)/3.7 )^1.11 + 6.9/Re )
    import math
    a = (rel_rough / 3.7) ** 1.11 if rel_rough and rel_rough > 0 else 0.0
    b = 6.9 / Re
    inv_sqrt_f = -1.8 * math.log10(a + b)
    f = 1.0 / (inv_sqrt_f ** 2)
    return f

def headloss_darcy(L: float, D: float, V: float,
                   epsilon: float = None, nu: float = None, g: float = None):
    """Devuelve dict con hf, f, Re, régimen."""
    if any(x is None or x <= 0 for x in [L, D, V]):
        raise ValueError("L, D y V deben ser > 0.")
    nu = nu if (nu and nu > 0) else NU_WATER
    g = g if (g and g > 0) else G_DEFAULT
    eps = epsilon if (epsilon and epsilon >= 0) else 0.0

    Re, reg = reynolds(V, D, nu)
    rel = (eps / D) if D > 0 else 0.0
    f = friction_factor(Re, rel)
    hf = f * (L / D) * (V * V) / (2.0 * g)
    return {"hf": hf, "f": f, "Re": Re, "regimen": reg}

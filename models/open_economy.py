# models/open_economy.py
"""
Sistema IS-LM-BP — Economia Aberta (Mundell-Fleming)

Mercados:
  IS: Y = C + I + G + NX
  LM: M/P = kY - hr
  BP: NX(e,Y,Y*) + CF(r,r*) = 0

Variáveis endógenas: Y, r, e (flex) ou Y, r, M (fixo)
"""

import numpy as np
from scipy.optimize import fsolve


# ══════════════════════════════════════════════
# COMPONENTES ESTRUTURAIS
# ══════════════════════════════════════════════

def consumo(c0, c1, Y, T):
    return c0 + c1 * (Y - T)

def investimento(I0, b, r):
    return I0 - b * r

def exportacoes(x0, x1, Y_star, e):
    """X = x0 + x1*Y* — e afeta competitividade (↑e = depreciação = ↑X)"""
    return x0 + x1 * Y_star * e

def importacoes(m0, m1, Y, e):
    """M_imp = m0 + m1*Y — ↑e encarece importações (↓M_imp)"""
    return m0 + m1 * Y / e

def exportacoes_liquidas(x0, x1, Y_star, m0, m1, Y, e):
    X   = exportacoes(x0, x1, Y_star, e)
    Imp = importacoes(m0, m1, Y, e)
    return X - Imp

def fluxo_capital(kf, r, r_star):
    """CF = kf*(r - r*) — mobilidade de capital"""
    return kf * (r - r_star)

def balanco_pagamentos(NX, CF):
    """BP = NX + CF"""
    return NX + CF


# ══════════════════════════════════════════════
# EQUAÇÕES DO SISTEMA
# ══════════════════════════════════════════════

def eq_IS(Y, r, e, c0, c1, T, I0, b, G, x0, x1, Y_star, m0, m1):
    """
    IS aberta: Y - C - I - G - NX = 0
    """
    C  = consumo(c0, c1, Y, T)
    I  = investimento(I0, b, r)
    NX = exportacoes_liquidas(x0, x1, Y_star, m0, m1, Y, e)
    return Y - C - I - G - NX

def eq_LM(Y, r, M, P, k, h):
    """
    LM: M/P - kY + hr = 0
    """
    return M / P - k * Y + h * r

def eq_BP(Y, r, e, x0, x1, Y_star, m0, m1, kf, r_star):
    """
    BP: NX + CF = 0
    """
    NX = exportacoes_liquidas(x0, x1, Y_star, m0, m1, Y, e)
    CF = fluxo_capital(kf, r, r_star)
    return NX + CF


# ══════════════════════════════════════════════
# SOLVER — CÂMBIO FLEXÍVEL
# ══════════════════════════════════════════════

def solve_flex(params):
    """
    Câmbio flexível: e se ajusta para BP = 0.
    Endógenas: Y, r, e
    Sistema 3x3: IS = 0, LM = 0, BP = 0
    """
    p = params

    def sistema(vars_):
        Y, r, e = vars_
        f1 = eq_IS(Y, r, e,
                   p["c0"], p["c1"], p["T"], p["I0"], p["b"], p["G"],
                   p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"])
        f2 = eq_LM(Y, r, p["M"], p["P"], p["k"], p["h"])
        f3 = eq_BP(Y, r, e,
                   p["x0"], p["x1"], p["Y_star"],
                   p["m0"], p["m1"], p["kf"], p["r_star"])
        return [f1, f2, f3]

    # Chute inicial
    Y0 = p.get("Yn", 1200.0)
    r0 = p["r_star"]
    e0 = p["e"]

    sol = fsolve(sistema, [Y0, r0, e0], full_output=True)
    Y_eq, r_eq, e_eq = sol[0]

    return _build_result(Y_eq, r_eq, e_eq, p, regime="flex")


# ══════════════════════════════════════════════
# SOLVER — CÂMBIO FIXO
# ══════════════════════════════════════════════

def solve_fixo(params):
    """
    Câmbio fixo: BC ajusta M para manter BP = 0.
    e = e_fixed (constante)
    Endógenas: Y, r, M_eq
    Sistema 3x3: IS = 0, LM(M_eq) = 0, BP = 0
    """
    p = params
    e = p["e_fixed"]

    def sistema(vars_):
        Y, r, M_eq = vars_
        f1 = eq_IS(Y, r, e,
                   p["c0"], p["c1"], p["T"], p["I0"], p["b"], p["G"],
                   p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"])
        f2 = eq_LM(Y, r, M_eq, p["P"], p["k"], p["h"])
        f3 = eq_BP(Y, r, e,
                   p["x0"], p["x1"], p["Y_star"],
                   p["m0"], p["m1"], p["kf"], p["r_star"])
        return [f1, f2, f3]

    Y0  = p.get("Yn", 1200.0)
    r0  = p["r_star"]
    M0  = p["M"]

    sol = fsolve(sistema, [Y0, r0, M0], full_output=True)
    Y_eq, r_eq, M_eq = sol[0]

    return _build_result(Y_eq, r_eq, e, p, regime="fixo", M_eq=M_eq)


# ══════════════════════════════════════════════
# RESULTADO COMPLETO
# ══════════════════════════════════════════════

def _build_result(Y, r, e, p, regime, M_eq=None):
    C   = consumo(p["c0"], p["c1"], Y, p["T"])
    I   = investimento(p["I0"], p["b"], r)
    NX  = exportacoes_liquidas(p["x0"], p["x1"], p["Y_star"],
                               p["m0"], p["m1"], Y, e)
    X   = exportacoes(p["x0"], p["x1"], p["Y_star"], e)
    Imp = importacoes(p["m0"], p["m1"], Y, e)
    CF  = fluxo_capital(p["kf"], r, p["r_star"])
    BP  = balanco_pagamentos(NX, CF)
    M_used = M_eq if M_eq is not None else p["M"]

    return dict(
        Y=Y, r=r, e=e,
        C=C, I=I, NX=NX,
        X=X, Imp=Imp,
        CF=CF, BP=BP,
        M_eq=M_used,
        regime=regime,
        # Verificações de consistência
        IS_residual=Y - C - I - p["G"] - NX,
        LM_residual=M_used / p["P"] - p["k"]*Y + p["h"]*r,
        BP_residual=BP,
    )


# ══════════════════════════════════════════════
# CURVAS PARA PLOTAGEM
# ══════════════════════════════════════════════

def curva_IS_aberta(Y_grid, e, c0, c1, T, I0, b, G,
                    x0, x1, Y_star, m0, m1):
    """
    IS: r = f(Y) — isolando r da equação IS
    Y = C + I + G + NX
    Y = c0 + c1(Y-T) + I0 - b*r + G + NX(e,Y,Y*)
    r = [c0 - c1*T + I0 + G + NX(e,Y,Y*) - (1-c1)*Y] / b
    """
    r_vals = []
    for Y in Y_grid:
        NX = exportacoes_liquidas(x0, x1, Y_star, m0, m1, Y, e)
        A  = c0 - c1*T + I0 + G + NX
        r  = (A - (1 - c1)*Y) / max(b, 1e-9)
        r_vals.append(r)
    return np.array(r_vals)


def curva_LM(Y_grid, M, P, k, h):
    """
    LM: r = (kY - M/P) / h
    """
    return (k * Y_grid - M / P) / max(h, 1e-9)


def curva_BP(Y_grid, e, x0, x1, Y_star, m0, m1, kf, r_star):
    """
    BP: NX + CF = 0
    NX(e,Y,Y*) + kf*(r - r*) = 0
    r = r* - NX(e,Y,Y*) / kf

    Inclinação:
      - kf grande → BP quase horizontal (alta mobilidade)
      - kf pequeno → BP íngreme (baixa mobilidade)
      - kf → ∞ → r = r* (mobilidade perfeita)
    """
    r_vals = []
    for Y in Y_grid:
        NX = exportacoes_liquidas(x0, x1, Y_star, m0, m1, Y, e)
        if kf > 1e6:  # mobilidade perfeita
            r_vals.append(r_star)
        else:
            r = r_star - NX / max(kf, 1e-9)
            r_vals.append(r)
    return np.array(r_vals)
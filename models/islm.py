import numpy as np

def solve_islm(c0, c1, T, I0, b, G, k, h, M, P):
    """
    Solução analítica simultânea IS-LM.

    IS: Y = mult*(c0 - c1*T + I0 + G) - mult*b*r
    LM: r = (k*Y - M/P) / h

    Substituindo LM na IS e resolvendo para Y*:
        Y* = [mult*A*h + mult*b*M/P] / [h + mult*b*k]
        r* = (k*Y* - M/P) / h
    """
    mult = 1.0 / max(1e-9, 1.0 - c1)
    A    = c0 - c1*T + I0 + G
    MP   = M / max(P, 1e-9)

    Y_eq = (mult * A * h + mult * b * MP) / max(h + mult * b * k, 1e-9)
    r_eq = (k * Y_eq - MP) / max(h, 1e-9)

    C_eq = c0 + c1 * (Y_eq - T)
    I_eq = I0 - b * r_eq
    S_eq = Y_eq - T - C_eq

    return dict(Y=Y_eq, r=r_eq, C=C_eq, I=I_eq, S=S_eq, mult=mult, A=A)


def curva_is(Y_grid, c0, c1, T, I0, b, G):
    """
    IS: r = [mult*(c0 - c1*T + I0 + G) - Y] / (mult*b)
    """
    mult = 1.0 / max(1e-9, 1.0 - c1)
    A    = c0 - c1*T + I0 + G
    r    = (mult * A - Y_grid) / max(mult * b, 1e-9)
    return r


def curva_lm(Y_grid, k, h, M, P):
    """
    LM: r = (k*Y - M/P) / h
    """
    MP = M / max(P, 1e-9)
    r  = (k * Y_grid - MP) / max(h, 1e-9)
    return r
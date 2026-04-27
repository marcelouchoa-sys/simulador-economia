import numpy as np

def resolver_oa_curto(Y_grid, Pe, Yn, alpha):
    """
    OA de Curto Prazo (Lucas / Síntese Neoclássica):
        P = Pe + (1/alpha)*(Y - Yn)
    Firmas ofertam mais se P > Pe (surpresa de preços).
    """
    P = Pe + (Y_grid - Yn) / max(alpha, 1e-9)
    eq = f"P = {Pe:.2f} + (Y − {Yn:.0f}) / {alpha:.0f}"
    return P, eq


def resolver_oa_longo(Yn):
    """
    OA de Longo Prazo (Clássica):
        Y = Yn  — linha vertical
    No longo prazo, produto = potencial independente de P.
    """
    return Yn


def hiato_produto(Y, Yn):
    """
    Hiato = Y - Yn
    Positivo → economia acima do potencial → pressão inflacionária
    Negativo → recessão
    """
    return Y - Yn
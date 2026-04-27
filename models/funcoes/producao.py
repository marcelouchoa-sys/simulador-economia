import numpy as np

def resolver_producao(K_grid, L, A=1.0, alpha=0.33, escola="Keynesiana"):
    """
    Função de Produção Cobb-Douglas:
        Y = A * K^alpha * L^(1-alpha)

    Clássica: mercados de fatores em equilíbrio, pleno emprego
    Keynesiana: L pode estar abaixo do pleno emprego (desemprego involuntário)
    """
    Y = A * (K_grid ** alpha) * (L ** (1.0 - alpha))
    eq = f"Y = {A:.1f} · K^{alpha:.2f} · L^{1-alpha:.2f}"
    return Y, eq


def produtividade_marginal_capital(K, L, A=1.0, alpha=0.33):
    """
    PMgK = alpha * A * (L/K)^(1-alpha)
    Determina a demanda por capital (= taxa de juros real no equilíbrio clássico)
    """
    return alpha * A * (L / max(K, 1e-9)) ** (1.0 - alpha)


def produtividade_marginal_trabalho(K, L, A=1.0, alpha=0.33):
    """
    PMgL = (1-alpha) * A * (K/L)^alpha
    Determina o salário real de equilíbrio
    """
    return (1.0 - alpha) * A * (K / max(L, 1e-9)) ** alpha
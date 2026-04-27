import numpy as np

def solve_phillips(Y_eq, Yn, Pe, alpha, u_natural=0.05, lambda_okun=2.0):
    """
    Sistema Phillips completo com microfundamentos.

    1. Hiato do produto
       gap = Y - Yn

    2. Lei de Okun (inversa):
       u - u_n = -gap / (lambda * Yn)
       u = u_n - gap / (lambda * Yn)

    3. Curva de Phillips Aceleracionista (Friedman-Phelps):
       pi = pi_e + gamma*(u_n - u)
       onde gamma = 1/(alpha * u_natural) — calibrado pelo modelo

    4. Expectativas:
       pi_e = dPe/Pe  (inflação esperada implícita)
    """
    gap   = Y_eq - Yn
    u     = max(0.001, u_natural - gap / max(lambda_okun * Yn, 1e-9))
    pi_e  = max(-0.5, (Pe - 1.0))          # inflação esperada implícita
    gamma = 1.0 / max(alpha * u_natural, 1e-9)
    pi    = pi_e + gamma * (u_natural - u)

    return dict(
        u=u,
        pi=pi,
        pi_e=pi_e,
        gap=gap,
        u_natural=u_natural,
        gamma=gamma
    )


def curva_phillips_cp(u_grid, pi_e, u_natural, gamma):
    """
    Phillips CP: pi = pi_e + gamma*(u_n - u)
    Para cada nível de pi_e, uma curva diferente.
    """
    return pi_e + gamma * (u_natural - u_grid)


def curva_phillips_lp(pi_grid, u_natural):
    """
    Phillips LP: u = u_natural para qualquer pi (vertical — NAIRU).
    """
    return np.full_like(pi_grid, u_natural)


def trajetoria_expectativas(pi_shocks, u_natural, gamma,
                             theta=0.5, n_periodos=20):
    """
    Dinâmica de expectativas adaptativas.
    theta: velocidade de ajuste (0=estático, 1=racional)

    pi_e(t+1) = pi_e(t) + theta*(pi(t) - pi_e(t))
    u(t)      = u_n - (pi(t) - pi_e(t)) / gamma
    """
    pi_e = 0.0
    trajetoria = []

    for t, pi_shock in enumerate(pi_shocks):
        pi_real = pi_e + pi_shock
        u_t     = u_natural - (pi_real - pi_e) / max(gamma, 1e-9)
        trajetoria.append(dict(t=t, pi=pi_real, pi_e=pi_e, u=u_t))
        pi_e = pi_e + theta * (pi_real - pi_e)

    return trajetoria
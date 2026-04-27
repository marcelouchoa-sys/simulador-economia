# core/parameters.py

DEFAULT_PARAMS = {
    # ── Consumo ──────────────────────────
    "c0":    100.0,   # consumo autônomo
    "c1":    0.75,    # propensão marginal a consumir

    # ── Investimento ─────────────────────
    "I0":    200.0,   # investimento autônomo
    "b":     50.0,    # sensibilidade do investimento à taxa de juros

    # ── Fiscal ───────────────────────────
    "G":     300.0,   # gasto do governo
    "T":     200.0,   # impostos

    # ── Monetário ────────────────────────
    "M":     1000.0,  # oferta monetária nominal
    "P":     1.0,     # nível de preços
    "k":     0.5,     # sensibilidade da demanda por moeda à renda
    "h":     100.0,   # sensibilidade da demanda por moeda à taxa de juros

    # ── Oferta Agregada ──────────────────
    "Pe":    1.0,     # expectativa de preços
    "Yn":    1200.0,  # produto potencial
    "alpha": 5.0,     # sensibilidade da OA CP ao hiato

    # ── Phillips / Okun ──────────────────
    "u_natural":   0.05,
    "lambda_okun": 2.0,
    "theta":       0.3,

    # ── Economia Aberta (IS-LM-BP) ───────
    "x0":    100.0,   # exportações autônomas
    "x1":    0.1,     # sensibilidade das exportações à renda externa
    "m0":    50.0,    # importações autônomas
    "m1":    0.15,    # propensão marginal a importar
    "kf":    200.0,   # mobilidade de capital (↑ = mais móvel)
    "r_star": 0.03,   # taxa de juros internacional
    "Y_star": 1500.0, # renda externa
    "e":     1.0,     # taxa de câmbio nominal (unidades domésticas/estrangeira)
    "e_fixed": 1.0,   # câmbio fixo de referência
    "regime": "flex", # "flex" ou "fixo"
}
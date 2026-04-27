# pages/4_🌍_Economia_Aberta.py
"""
IS-LM-BP — Economia Aberta (Mundell-Fleming)
Modo Simplificado (didático) + Modo Complexo (numérico)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════
# IMPORTAÇÕES SEGURAS (sem scipy)
# ══════════════════════════════════════════════════════════════
try:
    from scipy.optimize import fsolve
    SCIPY_OK = True
except ImportError:
    SCIPY_OK = False

from core.parameters import DEFAULT_PARAMS

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(layout="wide", page_title="IS-LM-BP")

# ══════════════════════════════════════════════════════════════
# NÚCLEO ECONÔMICO — EQUAÇÕES
# ══════════════════════════════════════════════════════════════

def consumo(c0, c1, Y, T):
    return c0 + c1 * (Y - T)

def investimento(I0, b, r):
    return I0 - b * r

def exportacoes(x0, x1, Y_star, e):
    return x0 + x1 * Y_star * e

def importacoes(m0, m1, Y, e):
    return m0 + m1 * Y / max(e, 1e-9)

def NX(x0, x1, Y_star, m0, m1, Y, e):
    return exportacoes(x0, x1, Y_star, e) - importacoes(m0, m1, Y, e)

def fluxo_capital(kf, r, r_star):
    return kf * (r - r_star)

def eq_IS(Y, r, e, p):
    C  = consumo(p["c0"], p["c1"], Y, p["T"])
    I  = investimento(p["I0"], p["b"], r)
    nx = NX(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e) if p.get("aberta") else 0.0
    return Y - C - I - p["G"] - nx

def eq_LM(Y, r, M, p):
    return M / p["P"] - p["k"] * Y + p["h"] * r

def eq_BP(Y, r, e, p):
    nx = NX(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e)
    cf = fluxo_capital(p["kf"], r, p["r_star"])
    return nx + cf

# ── Solver numérico (Newton-Raphson manual, sem scipy) ────────
def newton_solve(F, x0, tol=1e-10, max_iter=500):
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        fx = np.array(F(x), dtype=float)
        if np.max(np.abs(fx)) < tol:
            return x, True
        # Jacobiano numérico
        n  = len(x)
        J  = np.zeros((n, n))
        dx = 1e-6
        for j in range(n):
            xp = x.copy(); xp[j] += dx
            J[:, j] = (np.array(F(xp)) - fx) / dx
        try:
            delta = np.linalg.solve(J, -fx)
        except np.linalg.LinAlgError:
            return x, False
        x = x + delta
    return x, False

# ── Solver câmbio flexível ────────────────────────────────────
def solve_flex(p):
    def F(v):
        Y, r, e = v
        return [eq_IS(Y, r, e, p), eq_LM(Y, r, p["M"], p), eq_BP(Y, r, e, p)]
    x0  = [p.get("Yn", 1200.0), p["r_star"], p.get("e", 1.0)]
    sol, ok = newton_solve(F, x0)
    if not ok and SCIPY_OK:
        sol = fsolve(F, x0)
    Y, r, e = sol
    return _result(Y, r, e, p, "flex")

# ── Solver câmbio fixo ────────────────────────────────────────
def solve_fixo(p):
    e = p.get("e_fixed", 1.0)
    def F(v):
        Y, r, M_eq = v
        return [eq_IS(Y, r, e, p), eq_LM(Y, r, M_eq, p), eq_BP(Y, r, e, p)]
    x0  = [p.get("Yn", 1200.0), p["r_star"], p["M"]]
    sol, ok = newton_solve(F, x0)
    if not ok and SCIPY_OK:
        sol = fsolve(F, x0)
    Y, r, M_eq = sol
    return _result(Y, r, e, p, "fixo", M_eq=M_eq)

# ── Solver economia fechada ───────────────────────────────────
def solve_fechada(p):
    # IS fechada: Y = c0 + c1(Y-T) + I0 - b*r + G
    # LM: M/P = kY - h*r
    # Sistema 2x2 linear
    # (1-c1)*Y + b*r = c0 - c1*T + I0 + G  → IS
    # k*Y - h*r = M/P                        → LM
    A = np.array([
        [1 - p["c1"],  p["b"]],
        [p["k"],      -p["h"]]
    ])
    B = np.array([
        p["c0"] - p["c1"]*p["T"] + p["I0"] + p["G"],
        p["M"] / p["P"]
    ])
    try:
        sol = np.linalg.solve(A, B)
        Y, r = sol
    except np.linalg.LinAlgError:
        Y, r = p.get("Yn", 1200.0), p["r_star"]
    return _result(Y, r, p.get("e", 1.0), p, "fechada")

def _result(Y, r, e, p, regime, M_eq=None):
    C   = consumo(p["c0"], p["c1"], Y, p["T"])
    I   = investimento(p["I0"], p["b"], r)
    nx  = NX(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e) if p.get("aberta") else 0.0
    cf  = fluxo_capital(p["kf"], r, p["r_star"]) if p.get("aberta") else 0.0
    M_u = M_eq if M_eq is not None else p["M"]
    return dict(
        Y=Y, r=r, e=e, C=C, I=I, NX=nx, CF=cf,
        BP=nx+cf, M_eq=M_u, regime=regime,
        IS_res=Y - C - I - p["G"] - nx,
        LM_res=M_u/p["P"] - p["k"]*Y + p["h"]*r,
        BP_res=nx+cf if p.get("aberta") else 0.0,
    )

# ── Curvas para plotagem ──────────────────────────────────────
def curva_IS(Y_grid, e, p, aberta=True):
    r_vals = []
    for Y in Y_grid:
        nx = NX(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e) if aberta else 0.0
        A  = p["c0"] - p["c1"]*p["T"] + p["I0"] + p["G"] + nx
        r  = (A - (1 - p["c1"])*Y) / max(p["b"], 1e-9)
        r_vals.append(r)
    return np.array(r_vals)

def curva_LM(Y_grid, M, p):
    return (p["k"]*Y_grid - M/p["P"]) / max(p["h"], 1e-9)

def curva_BP_plot(Y_grid, e, p):
    r_vals = []
    for Y in Y_grid:
        nx = NX(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e)
        if p["kf"] > 1e6:
            r_vals.append(p["r_star"])
        else:
            r_vals.append(p["r_star"] - nx / max(p["kf"], 1e-9))
    return np.array(r_vals)

# ══════════════════════════════════════════════════════════════
# GERADOR DE EXPLICAÇÃO AUTOMÁTICA (MODO SIMPLIFICADO)
# ══════════════════════════════════════════════════════════════

def gerar_explicacao(tipo_eco, regime, politica, direcao):
    """
    Gera explicação passo a passo como um professor de macroeconomia.
    Retorna lista de passos com tipo: 'intro', 'curva', 'ponto', 'externo', 'conclusao'
    """
    exp = []
    fiscal = politica == "Fiscal"
    expansao = direcao == "Expansionista"
    aberta = tipo_eco == "Aberta"
    flex = regime == "Flexível"

    # ── INTRODUÇÃO ────────────────────────────────────────────
    if fiscal and expansao:
        exp.append(("intro", "🏛️ O governo adotou uma **política fiscal expansionista**."))
        exp.append(("intro", "Isso significa um **aumento nos gastos públicos (G↑)** ou uma **redução de impostos (T↓)**."))
        exp.append(("intro", "O efeito direto é um aumento na **demanda agregada** da economia."))
    elif fiscal and not expansao:
        exp.append(("intro", "🏛️ O governo adotou uma **política fiscal contracionista**."))
        exp.append(("intro", "Isso significa uma **redução nos gastos públicos (G↓)** ou um **aumento de impostos (T↑)**."))
        exp.append(("intro", "O efeito direto é uma **redução na demanda agregada** da economia."))
    elif not fiscal and expansao:
        exp.append(("intro", "🏦 O Banco Central adotou uma **política monetária expansionista**."))
        exp.append(("intro", "Isso significa um **aumento na oferta de moeda (M↑)**."))
        exp.append(("intro", "Com mais moeda disponível, os juros tendem a cair."))
    else:
        exp.append(("intro", "🏦 O Banco Central adotou uma **política monetária contracionista**."))
        exp.append(("intro", "Isso significa uma **redução na oferta de moeda (M↓)**."))
        exp.append(("intro", "Com menos moeda disponível, os juros tendem a subir."))

    # ── DESLOCAMENTO DA CURVA ─────────────────────────────────
    if fiscal:
        direcao_curva = "direita" if expansao else "esquerda"
        exp.append(("curva", f"📈 Como consequência, a **curva IS se desloca para a {direcao_curva}**."))
        exp.append(("curva", "A curva IS representa o equilíbrio no mercado de bens. "
                             "Quando a demanda aumenta, para cada nível de juros, o produto de equilíbrio é maior."))
        exp.append(("curva", "A curva **LM não se move** — a oferta de moeda não foi alterada."))
    else:
        direcao_curva = "direita" if expansao else "esquerda"
        exp.append(("curva", f"📈 Como consequência, a **curva LM se desloca para a {direcao_curva}**."))
        exp.append(("curva", "A curva LM representa o equilíbrio no mercado monetário. "
                             "Com mais moeda, para cada nível de renda, os juros de equilíbrio são menores."))
        exp.append(("curva", "A curva **IS não se move** — os gastos e impostos não foram alterados."))

    # ── PONTO A → B ───────────────────────────────────────────
    exp.append(("ponto", "📍 **Ponto A → Ponto B** (desequilíbrio transitório)"))
    if fiscal and expansao:
        exp.append(("ponto", "Com a IS deslocada para a direita, ao nível de juros do ponto A, "
                             "a demanda por bens **supera a produção atual**."))
        exp.append(("ponto", "Isso pressiona o produto para cima. Mas o aumento do produto "
                             "eleva a **demanda por moeda**, pressionando os **juros para cima**."))
        exp.append(("ponto", "O ponto B representa esse desequilíbrio: Y maior, r maior, "
                             "mas ainda fora do equilíbrio do mercado monetário."))
    elif fiscal and not expansao:
        exp.append(("ponto", "Com a IS deslocada para a esquerda, a demanda cai. "
                             "O produto começa a recuar e os juros caem."))
        exp.append(("ponto", "O ponto B representa a queda inicial: Y menor, r menor."))
    elif not fiscal and expansao:
        exp.append(("ponto", "Com a LM deslocada para a direita, ao nível de renda do ponto A, "
                             "há **excesso de oferta de moeda**."))
        exp.append(("ponto", "Isso reduz os juros. Com juros menores, o investimento aumenta, "
                             "elevando a demanda e o produto."))
        exp.append(("ponto", "O ponto B representa: r menor, Y maior — mas ainda em ajuste."))
    else:
        exp.append(("ponto", "Com a LM deslocada para a esquerda, há **escassez de moeda**."))
        exp.append(("ponto", "Os juros sobem. Com juros maiores, o investimento cai, "
                             "reduzindo a demanda e o produto."))
        exp.append(("ponto", "O ponto B representa: r maior, Y menor — em ajuste."))

    # ── PONTO B → C ───────────────────────────────────────────
    exp.append(("ponto", "📍 **Ponto B → Ponto C** (novo equilíbrio)"))
    exp.append(("ponto", "O sistema se ajusta automaticamente até que IS e LM se intersectem novamente."))
    if fiscal and expansao:
        exp.append(("ponto", "No ponto C: **Y maior e r maior** do que no ponto A. "
                             "O aumento dos juros **reduz parcialmente o investimento privado** — "
                             "esse é o efeito chamado de **crowding-out**."))
    elif fiscal and not expansao:
        exp.append(("ponto", "No ponto C: **Y menor e r menor** do que no ponto A."))
    elif not fiscal and expansao:
        exp.append(("ponto", "No ponto C: **Y maior e r menor** do que no ponto A. "
                             "A política monetária estimulou o investimento sem elevar os juros."))
    else:
        exp.append(("ponto", "No ponto C: **Y menor e r maior** do que no ponto A. "
                             "A contração monetária desaqueceu a economia."))

    # ── EFEITOS EXTERNOS (ECONOMIA ABERTA) ───────────────────
    if aberta:
        exp.append(("externo", "🌍 **Efeitos sobre a economia aberta:**"))

        if fiscal and expansao and flex:
            exp.append(("externo", "Com r maior, o país se torna mais atrativo para capital estrangeiro."))
            exp.append(("externo", "Há **entrada de capital (CF > 0)**, o que aprecia a moeda doméstica **(e↓)**."))
            exp.append(("externo", "Com câmbio apreciado, as exportações ficam mais caras e as importações mais baratas."))
            exp.append(("externo", "Isso **reduz as exportações líquidas (NX↓)**, deslocando a IS de volta para a esquerda."))
            exp.append(("externo", "⚠️ **Resultado Mundell-Fleming:** Com câmbio flexível e alta mobilidade de capital, "
                                   "a política fiscal é **ineficaz** — o crowding-out externo cancela o estímulo."))
        elif fiscal and expansao and not flex:
            exp.append(("externo", "Com r maior, há entrada de capital. O BC precisa **comprar divisas** para manter o câmbio fixo."))
            exp.append(("externo", "Isso **aumenta a oferta de moeda (M↑)**, deslocando a LM para a direita."))
            exp.append(("externo", "✅ **Resultado Mundell-Fleming:** Com câmbio fixo e alta mobilidade, "
                                   "a política fiscal é **muito eficaz** — o efeito é amplificado."))
        elif not fiscal and expansao and flex:
            exp.append(("externo", "Com r menor, o capital sai do país em busca de melhores retornos."))
            exp.append(("externo", "Há **saída de capital (CF < 0)**, o que **deprecia a moeda (e↑)**."))
            exp.append(("externo", "Com câmbio depreciado, as exportações ficam mais baratas e competitivas."))
            exp.append(("externo", "Isso **aumenta as exportações líquidas (NX↑)**, deslocando a IS para a direita."))
            exp.append(("externo", "✅ **Resultado Mundell-Fleming:** Com câmbio flexível e alta mobilidade, "
                                   "a política monetária é **muito eficaz** — o canal cambial amplifica o estímulo."))
        elif not fiscal and expansao and not flex:
            exp.append(("externo", "Com r menor, há saída de capital. O BC precisa **vender divisas** para manter o câmbio fixo."))
            exp.append(("externo", "Isso **reduz a oferta de moeda (M↓)**, revertendo o estímulo inicial."))
            exp.append(("externo", "⚠️ **Resultado Mundell-Fleming:** Com câmbio fixo, "
                                   "a política monetária é **ineficaz** — o BC perde o controle da moeda."))
        elif fiscal and not expansao and flex:
            exp.append(("externo", "Com r menor, há saída de capital e **depreciação cambial (e↑)**."))
            exp.append(("externo", "A depreciação estimula exportações **(NX↑)**, parcialmente compensando a contração fiscal."))
        elif not fiscal and not expansao and flex:
            exp.append(("externo", "Com r maior, há entrada de capital e **apreciação cambial (e↓)**."))
            exp.append(("externo", "A apreciação reduz exportações **(NX↓)**, amplificando a contração."))
        else:
            exp.append(("externo", "O BC ajusta a oferta de moeda para manter o câmbio fixo, "
                                   "alterando a eficácia da política."))

    # ── CONCLUSÃO ─────────────────────────────────────────────
    exp.append(("conclusao", "✅ **Conclusão:**"))
    if fiscal and expansao:
        if aberta and flex:
            exp.append(("conclusao", "A política fiscal expansionista em câmbio flexível com alta mobilidade de capital "
                                     "**não aumenta o produto** — o crowding-out externo é completo."))
        elif aberta and not flex:
            exp.append(("conclusao", "A política fiscal expansionista em câmbio fixo **é muito eficaz**, "
                                     "pois o BC valida o estímulo com expansão monetária."))
        else:
            exp.append(("conclusao", "A política fiscal expansionista **aumenta Y e r**. "
                                     "O crowding-out parcial reduz o investimento privado."))
    elif fiscal and not expansao:
        exp.append(("conclusao", "A política fiscal contracionista **reduz Y e r**, "
                                 "podendo ser usada para controlar inflação."))
    elif not fiscal and expansao:
        if aberta and flex:
            exp.append(("conclusao", "A política monetária expansionista em câmbio flexível **é muito eficaz** — "
                                     "atua via canal de juros E via canal cambial."))
        elif aberta and not flex:
            exp.append(("conclusao", "A política monetária expansionista em câmbio fixo **é ineficaz** — "
                                     "o BC perde autonomia para defender o câmbio."))
        else:
            exp.append(("conclusao", "A política monetária expansionista **aumenta Y e reduz r**, "
                                     "estimulando o investimento privado."))
    else:
        exp.append(("conclusao", "A política monetária contracionista **reduz Y e eleva r**, "
                                 "sendo usada para combater inflação."))

    return exp

# ══════════════════════════════════════════════════════════════
# GRÁFICO MODO SIMPLIFICADO
# ══════════════════════════════════════════════════════════════

def grafico_simplificado(politica, direcao, tipo_eco, regime):
    """
    Gráfico qualitativo IS-LM (sem números nos eixos).
    Mostra curvas base, curvas deslocadas, pontos A, B, C e setas.
    """
    fiscal   = politica == "Fiscal"
    expansao = direcao == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime == "Flexível"

    # Curvas base (normalizadas, sem unidade)
    Y = np.linspace(0.2, 1.8, 300)

    # IS base: r = 1.2 - 0.8*Y
    r_IS0 = 1.2 - 0.8 * Y
    # LM base: r = -0.4 + 0.6*Y
    r_LM0 = -0.4 + 0.6 * Y

    # Equilíbrio A: IS0 = LM0 → 1.2 - 0.8Y = -0.4 + 0.6Y → Y=1.143, r=0.286
    YA = (1.2 + 0.4) / (0.8 + 0.6)
    rA = 1.2 - 0.8 * YA

    # Deslocamento
    shift = 0.35

    if fiscal and expansao:
        r_IS1 = r_IS0 + shift   # IS desloca direita (↑)
        r_LM1 = r_LM0           # LM fica
        # Equilíbrio C: IS1 = LM0
        YC = (1.2 + shift + 0.4) / (0.8 + 0.6)
        rC = 1.2 + shift - 0.8 * YC
        # Ponto B: Y aumenta ao nível de juros de A
        YB = YC
        rB = rA
        curva_move = "IS"
    elif fiscal and not expansao:
        r_IS1 = r_IS0 - shift
        r_LM1 = r_LM0
        YC = (1.2 - shift + 0.4) / (0.8 + 0.6)
        rC = 1.2 - shift - 0.8 * YC
        YB = YC; rB = rA
        curva_move = "IS"
    elif not fiscal and expansao:
        r_IS1 = r_IS0
        r_LM1 = r_LM0 - shift   # LM desloca direita (↓ em r)
        YC = (1.2 + 0.4 - shift) / (0.8 + 0.6)
        rC = -0.4 - shift + 0.6 * YC
        YB = YA; rB = rA - shift
        curva_move = "LM"
    else:
        r_IS1 = r_IS0
        r_LM1 = r_LM0 + shift
        YC = (1.2 + 0.4 + shift) / (0.8 + 0.6)
        rC = -0.4 + shift + 0.6 * YC
        YB = YA; rB = rA + shift
        curva_move = "LM"

    # Efeito externo (câmbio flexível): IS retorna parcialmente
    r_IS2 = None
    YC_final = YC
    rC_final = rC

    if aberta and flex:
        if fiscal and expansao:
            # IS retorna para esquerda (crowding-out externo)
            r_IS2 = r_IS0 + shift * 0.15  # quase volta ao original
            YC_final = (1.2 + shift*0.15 + 0.4) / (0.8 + 0.6)
            rC_final = 1.2 + shift*0.15 - 0.8 * YC_final
        elif not fiscal and expansao:
            # IS desloca direita (canal cambial)
            r_IS2 = r_IS0 + shift * 0.7
            YC_final = (1.2 + shift*0.7 + 0.4 - shift) / (0.8 + 0.6)
            rC_final = -0.4 - shift + 0.6 * YC_final

    # ── Figura ────────────────────────────────────────────────
    fig = go.Figure()

    # Curvas base
    fig.add_trace(go.Scatter(
        x=Y, y=r_IS0, name="IS₀",
        line=dict(color="#1565c0", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=Y, y=r_LM0, name="LM₀",
        line=dict(color="#c62828", width=3)
    ))

    # BP (economia aberta)
    if aberta:
        r_BP0 = np.full_like(Y, 0.28)  # BP horizontal (alta mobilidade)
        fig.add_trace(go.Scatter(
            x=Y, y=r_BP0, name="BP",
            line=dict(color="#2e7d32", width=2.5, dash="dash")
        ))

    # Curvas deslocadas
    if curva_move == "IS":
        fig.add_trace(go.Scatter(
            x=Y, y=r_IS1, name="IS₁ (após choque)",
            line=dict(color="#1565c0", width=2.5, dash="dot")
        ))
    else:
        fig.add_trace(go.Scatter(
            x=Y, y=r_LM1, name="LM₁ (após choque)",
            line=dict(color="#c62828", width=2.5, dash="dot")
        ))

    # IS final (efeito câmbio)
    if r_IS2 is not None:
        fig.add_trace(go.Scatter(
            x=Y, y=r_IS2, name="IS₂ (ajuste cambial)",
            line=dict(color="#6a1b9a", width=2.5, dash="longdash")
        ))

    # Pontos A, B, C
    fig.add_trace(go.Scatter(
        x=[YA, YB, YC_final],
        y=[rA, rB, rC_final],
        mode="markers+text",
        marker=dict(size=14, color=["#1565c0", "#f57f17", "#2e7d32"],
                    symbol="circle", line=dict(width=2, color="white")),
        text=["A", "B", "C"],
        textposition=["top left", "top right", "bottom right"],
        textfont=dict(size=16, color=["#1565c0", "#f57f17", "#2e7d32"]),
        name="Equilíbrios",
        showlegend=True
    ))

    # Seta A → B
    fig.add_annotation(
        ax=YA, ay=rA, x=YB, y=rB,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2.5,
        arrowcolor="#f57f17"
    )
    # Seta B → C
    fig.add_annotation(
        ax=YB, ay=rB, x=YC_final, y=rC_final,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2.5,
        arrowcolor="#2e7d32"
    )

    # Layout sem números nos eixos
    fig.update_layout(
        title=f"IS-LM {'+ BP' if aberta else ''} — {politica} {direcao}",
        xaxis=dict(
            title="Produto (Y) →",
            showticklabels=False,
            showgrid=False,
            zeroline=True, zerolinecolor="#aaa"
        ),
        yaxis=dict(
            title="Taxa de Juros (r) →",
            showticklabels=False,
            showgrid=False,
            zeroline=True, zerolinecolor="#aaa"
        ),
        template="plotly_white",
        height=500,
        legend=dict(x=0.01, y=0.99),
        plot_bgcolor="#fafafa"
    )

    return fig

# ══════════════════════════════════════════════════════════════
# GRÁFICO MODO COMPLEXO
# ══════════════════════════════════════════════════════════════

def grafico_complexo(p_base, p_shock, eq_b, eq_c, aberta):
    Y_grid = np.linspace(200, 2500, 500)
    r_min, r_max = -0.3, 0.8

    r_IS_b = curva_IS(Y_grid, eq_b["e"], p_base, aberta)
    r_IS_c = curva_IS(Y_grid, eq_c["e"], p_shock, aberta)
    r_LM_b = curva_LM(Y_grid, p_base["M"], p_base)
    r_LM_c = curva_LM(Y_grid, p_shock["M"], p_shock)

    fig = go.Figure()

    for r_curve, name, color, dash in [
        (r_IS_b, "IS base",   "#1565c0", "solid"),
        (r_IS_c, "IS choque", "#1565c0", "dash"),
        (r_LM_b, "LM base",   "#c62828", "solid"),
        (r_LM_c, "LM choque", "#c62828", "dash"),
    ]:
        mask = (r_curve > r_min) & (r_curve < r_max)
        fig.add_trace(go.Scatter(
            x=Y_grid[mask], y=r_curve[mask],
            name=name, line=dict(color=color, width=2.5, dash=dash)
        ))

    if aberta:
        r_BP_b = curva_BP_plot(Y_grid, eq_b["e"], p_base)
        r_BP_c = curva_BP_plot(Y_grid, eq_c["e"], p_shock)
        for r_curve, name, dash in [
            (r_BP_b, "BP base",   "solid"),
            (r_BP_c, "BP choque", "dash"),
        ]:
            mask = (r_curve > r_min) & (r_curve < r_max)
            fig.add_trace(go.Scatter(
                x=Y_grid[mask], y=r_curve[mask],
                name=name, line=dict(color="#2e7d32", width=2.5, dash=dash)
            ))

    # Equilíbrios
    fig.add_trace(go.Scatter(
        x=[eq_b["Y"], eq_c["Y"]],
        y=[eq_b["r"], eq_c["r"]],
        mode="markers+text",
        marker=dict(size=14, color=["#1565c0", "#c62828"],
                    symbol="star", line=dict(width=1, color="white")),
        text=["E₀", "E₁"], textposition="top right",
        textfont=dict(size=14),
        name="Equilíbrios"
    ))

    # Seta
    fig.add_annotation(
        ax=eq_b["Y"], ay=eq_b["r"],
        x=eq_c["Y"],  y=eq_c["r"],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2.5,
        arrowcolor="black"
    )

    fig.update_layout(
        title="IS-LM-BP: Base vs. Choque",
        xaxis_title="Produto (Y)",
        yaxis_title="Taxa de Juros (r)",
        template="plotly_white",
        height=520,
        legend=dict(x=0.01, y=0.99)
    )
    return fig

# ══════════════════════════════════════════════════════════════
# INTERFACE PRINCIPAL
# ══════════════════════════════════════════════════════════════

st.title("🌍 IS-LM-BP — Simulador Macroeconômico")
st.caption("Mundell-Fleming | Economia Aberta | Rigor Teórico")

# ── ESCOLHA DO MODO ───────────────────────────────────────────
st.divider()
modo = st.radio(
    "### Escolha o modo de simulação:",
    ["🎓 Modo Simplificado (didático, sem números)",
     "🔢 Modo Complexo (numérico, com equações)"],
    horizontal=True
)
st.divider()

# ══════════════════════════════════════════════════════════════
# MODO SIMPLIFICADO
# ══════════════════════════════════════════════════════════════
if "Simplificado" in modo:

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ⚙️ Configuração")

        tipo_eco = st.radio("Tipo de economia:", ["Fechada", "Aberta"])
        aberta   = tipo_eco == "Aberta"

        regime = "Flexível"
        if aberta:
            regime = st.radio("Regime cambial:", ["Flexível", "Fixo"])

        st.divider()

        politica = st.radio("Tipo de política:", ["Fiscal", "Monetária"])
        direcao  = st.radio("Direção:", ["Expansionista", "Contracionista"])

        st.divider()
        executar = st.button("▶️ Simular", type="primary", use_container_width=True)

    with col2:
        if executar or st.session_state.get("simp_executado"):
            st.session_state["simp_executado"] = True
            st.session_state["simp_config"] = (tipo_eco, regime, politica, direcao)

        if st.session_state.get("simp_executado"):
            tipo_eco_s, regime_s, politica_s, direcao_s = st.session_state["simp_config"]

            # Gráfico
            fig = grafico_simplificado(politica_s, direcao_s, tipo_eco_s, regime_s)
            st.plotly_chart(fig, use_container_width=True)

            # Legenda dos pontos
            col_a, col_b, col_c = st.columns(3)
            col_a.info("🔵 **Ponto A**\nEquilíbrio inicial")
            col_b.warning("🟡 **Ponto B**\nDesequilíbrio transitório")
            col_c.success("🟢 **Ponto C**\nNovo equilíbrio")

        else:
            st.info("Configure os parâmetros ao lado e clique em **▶️ Simular**.")

    # ── EXPLICAÇÃO AUTOMÁTICA ─────────────────────────────────
    if st.session_state.get("simp_executado"):
        tipo_eco_s, regime_s, politica_s, direcao_s = st.session_state["simp_config"]
        st.divider()
        st.markdown("### 📖 Explicação Econômica Passo a Passo")

        explicacao = gerar_explicacao(tipo_eco_s, regime_s, politica_s, direcao_s)

        tipo_anterior = None
        for tipo, texto in explicacao:
            if tipo != tipo_anterior:
                if tipo == "intro":
                    st.markdown("#### 1️⃣ O que aconteceu?")
                elif tipo == "curva":
                    st.markdown("#### 2️⃣ Qual curva se move?")
                elif tipo == "ponto":
                    st.markdown("#### 3️⃣ Trajetória do equilíbrio")
                elif tipo == "externo":
                    st.markdown("#### 4️⃣ Efeitos sobre o setor externo")
                elif tipo == "conclusao":
                    st.markdown("#### 5️⃣ Conclusão")
                tipo_anterior = tipo

            if tipo == "conclusao":
                st.success(texto)
            elif tipo == "externo" and ("⚠️" in texto or "✅" in texto):
                if "⚠️" in texto:
                    st.warning(texto)
                else:
                    st.success(texto)
            else:
                st.markdown(f"→ {texto}")

# ══════════════════════════════════════════════════════════════
# MODO COMPLEXO
# ══════════════════════════════════════════════════════════════
else:
    # ── Parâmetros ────────────────────────────────────────────
    p = DEFAULT_PARAMS.copy()
    p["aberta"] = False

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🏛️ Política Econômica")
        p["G"] = st.number_input("G — Gasto do Governo", value=float(p["G"]), step=10.0)
        p["T"] = st.number_input("T — Impostos",         value=float(p["T"]), step=10.0)
        p["M"] = st.number_input("M — Oferta Monetária", value=float(p["M"]), step=50.0)
        p["P"] = st.number_input("P — Nível de Preços",  value=float(p["P"]), step=0.1)

        st.markdown("#### 📐 Parâmetros Estruturais")
        p["c0"] = st.number_input("c0 — Consumo Autônomo",     value=float(p["c0"]), step=10.0)
        p["c1"] = st.number_input("c1 — Propensão a Consumir", value=float(p["c1"]), step=0.01, format="%.2f")
        p["I0"] = st.number_input("I0 — Investimento Autônomo",value=float(p["I0"]), step=10.0)
        p["b"]  = st.number_input("b — Sensibilidade I a r",   value=float(p["b"]),  step=5.0)
        p["k"]  = st.number_input("k — Sensibilidade L a Y",   value=float(p["k"]),  step=0.05, format="%.2f")
        p["h"]  = st.number_input("h — Sensibilidade L a r",   value=float(p["h"]),  step=10.0)

    with col2:
        st.markdown("#### 🌐 Economia Aberta")
        aberta_cx = st.checkbox("Ativar economia aberta (IS-LM-BP)", value=False)
        p["aberta"] = aberta_cx

        if aberta_cx:
            regime_cx = st.radio("Regime cambial:", ["flex", "fixo"],
                                  format_func=lambda x: "Câmbio Flexível" if x == "flex" else "Câmbio Fixo")
            p["regime"] = regime_cx

            p["Y_star"]  = st.number_input("Y* — Renda Externa",        value=float(p["Y_star"]), step=50.0)
            p["r_star"]  = st.number_input("r* — Juros Internacionais",  value=float(p["r_star"]), step=0.005, format="%.4f")
            p["e"]       = st.number_input("e — Câmbio Inicial",         value=float(p["e"]),      step=0.05)
            p["x0"]      = st.number_input("x0 — Exportações Autônomas", value=float(p["x0"]),     step=10.0)
            p["x1"]      = st.number_input("x1 — Sensib. X a Y*",        value=float(p["x1"]),     step=0.01, format="%.3f")
            p["m0"]      = st.number_input("m0 — Importações Autônomas", value=float(p["m0"]),     step=10.0)
            p["m1"]      = st.number_input("m1 — Propensão a Importar",  value=float(p["m1"]),     step=0.01, format="%.3f")

            kf_preset = st.select_slider("Mobilidade de Capital:",
                                          options=["Baixa","Moderada","Alta","Perfeita"],
                                          value="Alta")
            p["kf"] = {"Baixa":50.0,"Moderada":200.0,"Alta":800.0,"Perfeita":1e7}[kf_preset]

            if regime_cx == "fixo":
                p["e_fixed"] = st.number_input("e fixo (meta BC)", value=float(p.get("e_fixed",1.0)), step=0.05)

    with col3:
        st.markdown("#### 🔀 Choque (Cenário 2)")
        dG = st.number_input("ΔG", value=0.0, step=10.0)
        dT = st.number_input("ΔT", value=0.0, step=10.0)
        dM = st.number_input("ΔM", value=0.0, step=50.0)
        if aberta_cx:
            dr_star = st.number_input("Δr*", value=0.0, step=0.005, format="%.4f")
            dY_star = st.number_input("ΔY*", value=0.0, step=50.0)
        else:
            dr_star = dY_star = 0.0

        executar_cx = st.button("🚀 Calcular Equilíbrio", type="primary", use_container_width=True)

    # ── Cálculo ───────────────────────────────────────────────
    if executar_cx:
        p_shock = p.copy()
        p_shock["G"]      += dG
        p_shock["T"]      += dT
        p_shock["M"]      += dM
        p_shock["r_star"] += dr_star
        p_shock["Y_star"] += dY_star

        try:
            if not aberta_cx:
                eq_b = solve_fechada(p)
                eq_c = solve_fechada(p_shock)
            elif p["regime"] == "flex":
                eq_b = solve_flex(p)
                eq_c = solve_flex(p_shock)
            else:
                eq_b = solve_fixo(p)
                eq_c = solve_fixo(p_shock)

            st.divider()
            st.markdown("### 📊 Resultados")

            # Métricas base
            st.markdown("**Cenário Base:**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Y*",  f"{eq_b['Y']:.2f}")
            c2.metric("r*",  f"{eq_b['r']*100:.3f}%")
            c3.metric("e*",  f"{eq_b['e']:.4f}")
            c4.metric("NX",  f"{eq_b['NX']:.2f}")

            # Tabela comparativa
            st.markdown("**Comparação Base vs. Choque:**")
            st.markdown(f"""
| Variável | Base | Choque | Δ |
|---|---|---|---|
| **Y** | {eq_b['Y']:.2f} | {eq_c['Y']:.2f} | **{eq_c['Y']-eq_b['Y']:+.2f}** |
| **r** | {eq_b['r']*100:.3f}% | {eq_c['r']*100:.3f}% | **{(eq_c['r']-eq_b['r'])*100:+.3f}pp** |
| **e** | {eq_b['e']:.4f} | {eq_c['e']:.4f} | **{eq_c['e']-eq_b['e']:+.4f}** |
| **NX** | {eq_b['NX']:.2f} | {eq_c['NX']:.2f} | **{eq_c['NX']-eq_b['NX']:+.2f}** |
| **CF** | {eq_b['CF']:.2f} | {eq_c['CF']:.2f} | **{eq_c['CF']-eq_b['CF']:+.2f}** |
| **C** | {eq_b['C']:.2f} | {eq_c['C']:.2f} | **{eq_c['C']-eq_b['C']:+.2f}** |
| **I** | {eq_b['I']:.2f} | {eq_c['I']:.2f} | **{eq_c['I']-eq_b['I']:+.2f}** |
""")

            # Consistência
            with st.expander("🔬 Verificação de Consistência"):
                for label, res in [("IS", eq_c["IS_res"]), ("LM", eq_c["LM_res"]), ("BP", eq_c["BP_res"])]:
                    ok = abs(res) < 0.01
                    st.markdown(f"{'✅' if ok else '⚠️'} **{label}** resíduo = `{res:.6f}`")

            # Gráfico
            fig = grafico_complexo(p, p_shock, eq_b, eq_c, aberta_cx)
            st.plotly_chart(fig, use_container_width=True)

            # Equações (modo avançado)
            with st.expander("📐 Equações do Sistema"):
                st.markdown(f"""
**IS (aberta):**
$$Y = c_0 + c_1(Y-T) + I_0 - br + G + NX(e,Y,Y^*)$$

**LM:**
$$\\frac{{M}}{{P}} = kY - hr$$

**BP:**
$$NX(e,Y,Y^*) + k_f(r - r^*) = 0$$

**Equilíbrio resolvido numericamente (Newton-Raphson):**
- $Y^* = {eq_c['Y']:.4f}$
- $r^* = {eq_c['r']:.6f}$
- $e^* = {eq_c['e']:.6f}$
""")

        except Exception as ex:
            st.error(f"Erro no solver: {ex}")
            st.info("Verifique os parâmetros — o sistema pode não ter solução com esses valores.")
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.parameters import DEFAULT_PARAMS
from models.funcoes.consumo import (
    resolver_consumo, resolver_poupanca,
    multiplicador_fiscal, multiplicador_imposto
)
from models.funcoes.investimento import resolver_investimento, efeito_crowding_out
from models.funcoes.demanda_moeda import resolver_demanda_moeda, resolver_lm
from models.funcoes.oferta_moeda import resolver_oferta_moeda
from models.funcoes.demanda_agregada import resolver_da
from models.funcoes.oferta_agregada import resolver_oa_curto, resolver_oa_longo, hiato_produto
from models.funcoes.producao import resolver_producao, produtividade_marginal_capital

st.set_page_config(layout="wide")

# ── Estado global ────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
p = st.session_state.params

# ── Cabeçalho ────────────────────────────────────────────────
st.title("📚 Funções Macroeconômicas")
st.caption("Cada parâmetro alterado aqui atualiza o sistema IS-LM-BP automaticamente.")

# ── Escola ───────────────────────────────────────────────────
escola = st.radio(
    "Abordagem teórica:",
    ["Keynesiana", "Clássica"],
    horizontal=True
)

ESCOLA_INFO = {
    "Keynesiana": "Demanda efetiva determina o produto. Rigidezes nominais. Desemprego involuntário possível. Política fiscal eficaz.",
    "Clássica":   "Oferta determina o produto (Lei de Say). Mercados se equilibram. Pleno emprego no longo prazo. Política fiscal ineficaz (crowding-out total)."
}
st.info(f"**{escola}:** {ESCOLA_INFO[escola]}")

# ── Função ───────────────────────────────────────────────────
funcao = st.selectbox("Selecione a função:", [
    "Consumo",
    "Poupança",
    "Investimento",
    "Demanda por Moeda",
    "Oferta de Moeda",
    "Demanda Agregada",
    "Oferta Agregada",
    "Produção"
])

st.divider()

# ── Grids ────────────────────────────────────────────────────
Y_grid = np.linspace(100, 2000, 300)
r_grid = np.linspace(0.001, 0.25, 300)
P_grid = np.linspace(0.2, 3.0, 300)
K_grid = np.linspace(100, 5000, 300)

# ============================================================
# CONSUMO
# ============================================================
if funcao == "Consumo":
    col1, col2 = st.columns([1, 2])
    with col1:
        c0 = st.slider("Consumo Autônomo (c0)", 0.0, 500.0, float(p["c0"]), 10.0)
        c1 = st.slider("Propensão Marginal a Consumir (c1)", 0.01, 0.99, float(p["c1"]), 0.01)
        T  = st.slider("Impostos (T)", 0.0, 500.0, float(p["T"]), 10.0)
        p["c0"], p["c1"], p["T"] = c0, c1, T

        mult_G = multiplicador_fiscal(c1)
        mult_T = multiplicador_imposto(c1)

        st.metric("Multiplicador Fiscal (ΔY/ΔG)", f"{mult_G:.3f}")
        st.metric("Multiplicador de Impostos (ΔY/ΔT)", f"{mult_T:.3f}")

        if escola == "Clássica":
            st.warning("Na visão Clássica, o multiplicador é neutralizado pelo crowding-out total.")

    with col2:
        C, eq_c = resolver_consumo(Y_grid, c0, c1, T, escola)
        S       = resolver_poupanca(Y_grid, c0, c1, T, escola)

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Função Consumo C(Y)", "Função Poupança S(Y)"))

        fig.add_trace(go.Scatter(x=Y_grid, y=C, name="C(Y)",
                                 line=dict(color="#1565c0", width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=Y_grid, y=Y_grid - T,
                                 name="Yd (45°)", line=dict(dash="dot", color="gray")), row=1, col=1)
        fig.add_trace(go.Scatter(x=Y_grid, y=S, name="S(Y)",
                                 line=dict(color="#2e7d32", width=2.5)), row=1, col=2)
        fig.add_hline(y=0, line=dict(color="black", width=1), row=1, col=2)

        fig.update_xaxes(title_text="Renda (Y)")
        fig.update_yaxes(title_text="C", row=1, col=1)
        fig.update_yaxes(title_text="S", row=1, col=2)
        fig.update_layout(height=420, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**Equação:** ${eq_c}$

**Identidade:** $S \\equiv Y - T - C = -{c0:.0f} + {1-c1:.2f}(Y - {T:.0f})$

**Interdependência sistêmica:**
- c₁ = {c1:.2f} → Multiplicador = **{mult_G:.3f}**
- Esse multiplicador define a **inclinação da curva IS**
- Alteração aqui propaga para IS-LM-BP automaticamente
""")

# ============================================================
# POUPANÇA
# ============================================================
elif funcao == "Poupança":
    c0, c1, T = p["c0"], p["c1"], p["T"]
    S = resolver_poupanca(Y_grid, c0, c1, T, escola)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Y_grid, y=S, name="S(Y)",
                             line=dict(color="#2e7d32", width=2.5)))
    fig.add_hline(y=0, line=dict(color="black", width=1))
    fig.update_layout(title="S(Y) — Função Poupança",
                      xaxis_title="Renda (Y)", yaxis_title="Poupança (S)",
                      template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**Identidade Contábil:** $S \\equiv Y - T - C$

$S = -{c0:.0f} + {1-c1:.2f}(Y - {T:.0f})$

**Propensão Marginal a Poupar:** $1 - c_1 = {1-c1:.2f}$

**Nota:** S não é uma função comportamental independente — é derivada de C.
{"**Clássico:** S determina I via mercado de fundos emprestáveis (taxa de juros equilibra S=I)." if escola == "Clássica" else "**Keynesiano:** I determina S via multiplicador (paradoxo da parcimônia)."}
""")

# ============================================================
# INVESTIMENTO
# ============================================================
elif funcao == "Investimento":
    col1, col2 = st.columns([1, 2])
    with col1:
        I0 = st.slider("Investimento Autônomo (I0)", 0.0, 500.0, float(p["I0"]), 10.0)
        b  = st.slider("Sensibilidade ao Juros (b)", 1.0, 300.0, float(p["b"]), 5.0)
        r_ref = st.slider("Juros de referência (r base)", 0.01, 0.20, float(p.get("r_world", 0.03)), 0.01)
        p["I0"], p["b"] = I0, b

        I_ref = I0 - b * r_ref
        st.metric("I no juros de referência", f"{I_ref:.1f}")
        st.metric("ΔI por +1p.p. de juros", f"{-b*0.01:.1f}")

    with col2:
        I, eq_i = resolver_investimento(r_grid, I0, b, escola)
        dI = efeito_crowding_out(r_ref, r_ref + 0.01, b)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r_grid * 100, y=I, name="I(r)",
                                 line=dict(color="#c62828", width=2.5)))
        fig.add_vline(x=r_ref * 100, line=dict(dash="dot", color="gray"))
        fig.update_layout(title="I(r) — Função Investimento",
                          xaxis_title="Taxa de Juros r (%)",
                          yaxis_title="Investimento (I)",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**Equação:** ${eq_i}$

**Interdependência sistêmica:**
- b = {b:.0f} → define a **inclinação da curva IS**
- IS mais inclinada quando b é maior (I mais sensível a r)
- Canal de transmissão da política monetária: ↑M → ↓r → ↑I → ↑Y

{"**Clássico:** I é determinado pela poupança agregada. Política monetária afeta apenas P, não Y." if escola == "Clássica" else "**Keynesiano:** I depende de expectativas (animal spirits) + juros. Instabilidade inerente."}
""")

# ============================================================
# DEMANDA POR MOEDA
# ============================================================
elif funcao == "Demanda por Moeda":
    col1, col2 = st.columns([1, 2])
    with col1:
        k = st.slider("Sensibilidade à Renda (k)", 0.1, 1.5, float(p["k"]), 0.05)
        h = st.slider("Sensibilidade ao Juros (h)", 10.0, 300.0, float(p["h"]), 10.0)
        Y_ref = st.slider("Renda de referência (Y)", 500.0, 1500.0, 1000.0, 50.0)
        p["k"], p["h"] = k, h

        Md_ref, eq_md = resolver_demanda_moeda(
            np.array([Y_ref]), r_grid, k, h, p["P"], escola
        )
        st.metric("Md/P em Y=" + str(int(Y_ref)) + ", r=5%", f"{float(k*Y_ref - h*0.05):.1f}")

    with col2:
        Md_Y1, _ = resolver_demanda_moeda(np.array([800.0]),  r_grid, k, h, p["P"], escola)
        Md_Y2, _ = resolver_demanda_moeda(np.array([1000.0]), r_grid, k, h, p["P"], escola)
        Md_Y3, _ = resolver_demanda_moeda(np.array([1200.0]), r_grid, k, h, p["P"], escola)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r_grid*100, y=Md_Y1, name="Md (Y=800)",
                                 line=dict(color="#1565c0", width=2)))
        fig.add_trace(go.Scatter(x=r_grid*100, y=Md_Y2, name="Md (Y=1000)",
                                 line=dict(color="#c62828", width=2)))
        fig.add_trace(go.Scatter(x=r_grid*100, y=Md_Y3, name="Md (Y=1200)",
                                 line=dict(color="#2e7d32", width=2)))
        fig.update_layout(title="Md(r) — Demanda por Moeda para diferentes Y",
                          xaxis_title="Taxa de Juros r (%)",
                          yaxis_title="Md/P (demanda real por moeda)",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**Equação:** ${eq_md}$

**Interdependência sistêmica:**
- k = {k:.2f} e h = {h:.0f} definem a **inclinação da curva LM**
- LM vertical quando h → 0 (armadilha da liquidez inexistente)
- LM horizontal quando h → ∞ (armadilha da liquidez keynesiana)

{"**Clássico (TQM):** MV = PY → Md = (1/V)·PY. Sem motivo especulação. Velocidade constante." if escola == "Clássica" else "**Keynesiano:** Três motivos (transação, precaução, especulação). h > 0 é essencial."}
""")

# ============================================================
# OFERTA DE MOEDA
# ============================================================
elif funcao == "Oferta de Moeda":
    col1, col2 = st.columns([1, 2])
    with col1:
        M   = st.slider("Oferta Nominal de Moeda (M)", 100.0, 1500.0, float(p["M"]), 50.0)
        P_v = st.slider("Nível de Preços (P)", 0.5, 3.0, float(p["P"]), 0.1)
        regime = st.radio("Regime da Oferta", ["Exógena", "Endógena"])
        p["M"], p["P"] = M, P_v

        MP, eq_ms = resolver_oferta_moeda(M, P_v, regime)
        st.metric("Oferta Real de Moeda (M/P)", f"{MP:.2f}")

    with col2:
        Md_eq, _ = resolver_demanda_moeda(np.array([1000.0]), r_grid, p["k"], p["h"], P_v, escola)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r_grid*100, y=Md_eq, name="Md (Y=1000)",
                                 line=dict(color="#1565c0", width=2.5)))
        fig.add_vline(x=0, line=dict(color="gray"))
        fig.add_hline(y=MP, line=dict(color="#c62828", width=2.5, dash="dash"),
                      annotation_text=f"Ms/P = {MP:.2f}")
        fig.update_layout(title="Equilíbrio no Mercado Monetário",
                          xaxis_title="Taxa de Juros r (%)",
                          yaxis_title="M/P",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**{eq_ms}**

**Interdependência sistêmica:**
- ↑ M → ↑ M/P → LM desloca para direita → ↓ r → ↑ I → ↑ Y
- {"**Clássico:** ↑ M → apenas ↑ P (neutralidade da moeda). Dicotomia clássica." if escola == "Clássica" else "**Keynesiano:** ↑ M pode ser ineficaz se h → ∞ (armadilha da liquidez)."}
""")

# ============================================================
# DEMANDA AGREGADA
# ============================================================
elif funcao == "Demanda Agregada":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Parâmetros IS-LM (herdados do sistema):**")
        c0 = st.number_input("c0", value=float(p["c0"]))
        c1 = st.number_input("c1", value=float(p["c1"]))
        T  = st.number_input("T",  value=float(p["T"]))
        I0 = st.number_input("I0", value=float(p["I0"]))
        b  = st.number_input("b",  value=float(p["b"]))
        G  = st.number_input("G",  value=float(p["G"]))
        k  = st.number_input("k",  value=float(p["k"]))
        h  = st.number_input("h",  value=float(p["h"]))
        M  = st.number_input("M",  value=float(p["M"]))
        p.update({"c0":c0,"c1":c1,"T":T,"I0":I0,"b":b,"G":G,"k":k,"h":h,"M":M})

    with col2:
        Y_da = resolver_da(P_grid, c0, c1, T, I0, b, G, k, h, M)
        Y_da_G = resolver_da(P_grid, c0, c1, T, I0, b, G+100, k, h, M)
        Y_da_M = resolver_da(P_grid, c0, c1, T, I0, b, G, k, h, M+200)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Y_da,   y=P_grid, name="DA Base",
                                 line=dict(color="#1565c0", width=2.5)))
        fig.add_trace(go.Scatter(x=Y_da_G, y=P_grid, name="DA (ΔG=+100)",
                                 line=dict(color="#c62828", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=Y_da_M, y=P_grid, name="DA (ΔM=+200)",
                                 line=dict(color="#2e7d32", width=2, dash="dot")))
        fig.update_layout(title="DA(P) — Derivada do Sistema IS-LM",
                          xaxis_title="Produto (Y)",
                          yaxis_title="Nível de Preços (P)",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
**A DA não é uma curva ad-hoc** — é o locus de equilíbrios IS-LM para cada P.

$Y^* = \\frac{\\text{mult} \\cdot A + \\text{mult} \\cdot b \\cdot M/(hP)}{1 + \\text{mult} \\cdot bk/h}$

**Interdependência:** qualquer parâmetro IS ou LM desloca a DA.
""")

# ============================================================
# OFERTA AGREGADA
# ============================================================
elif funcao == "Oferta Agregada":
    col1, col2 = st.columns([1, 2])
    with col1:
        Pe    = st.slider("Expectativa de Preços (Pe)", 0.5, 3.0, float(p["Pe"]), 0.1)
        Yn    = st.slider("Produto Potencial (Yn)",    500.0, 2000.0, float(p["Yn"]), 50.0)
        alpha = st.slider("Sensibilidade P/Y (α)",     10.0, 500.0, float(p["alpha"]), 10.0)
        p["Pe"], p["Yn"], p["alpha"] = Pe, Yn, alpha

    with col2:
        P_oa, eq_oa = resolver_oa_curto(Y_grid, Pe, Yn, alpha)
        P_oa2, _    = resolver_oa_curto(Y_grid, Pe * 1.2, Yn, alpha)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Y_grid, y=P_oa,  name=f"OA CP (Pe={Pe:.2f})",
                                 line=dict(color="#c62828", width=2.5)))
        fig.add_trace(go.Scatter(x=Y_grid, y=P_oa2, name=f"OA CP (Pe={Pe*1.2:.2f})",
                                 line=dict(color="#e65100", width=2, dash="dash")))
        fig.add_vline(x=Yn, line=dict(color="black", width=2, dash="dot"),
                      annotation_text=f"Yn={Yn:.0f}")
        fig.update_layout(title="OA — Curto e Longo Prazo",
                          xaxis_title="Produto (Y)",
                          yaxis_title="Nível de Preços (P)",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    Y_atual = p.get("Y_eq", Yn)
    hiato = hiato_produto(Y_atual, Yn)
    st.metric("Hiato do Produto (Y - Yn)", f"{hiato:+.1f}")
    st.markdown(f"""
**Equação:** ${eq_oa}$

**Longo Prazo (Clássico):** $Y = Y_n = {Yn:.0f}$ (vertical)

**Interdependência:**
- Pe sobe → OA sobe → P sobe → M/P cai → LM contrai → Y cai de volta a Yn
- Mecanismo de ajuste automático de longo prazo
""")

# ============================================================
# PRODUÇÃO
# ============================================================
elif funcao == "Produção":
    col1, col2 = st.columns([1, 2])
    with col1:
        A     = st.slider("Produtividade Total (A)", 0.5, 3.0, 1.0, 0.1)
        alpha = st.slider("Participação do Capital (α)", 0.1, 0.9, 0.33, 0.01)
        L     = st.slider("Trabalho (L)", 10.0, 500.0, 100.0, 10.0)

        PMgK = produtividade_marginal_capital(1000.0, L, A, alpha)
        st.metric("PMgK (K=1000)", f"{PMgK:.4f}")
        st.caption("No equilíbrio clássico: PMgK = r (taxa de juros real)")

    with col2:
        Y_prod, eq_prod = resolver_producao(K_grid, L, A, alpha, escola)
        Y_prod2, _      = resolver_producao(K_grid, L * 1.2, A, alpha, escola)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=K_grid, y=Y_prod,  name=f"Y(K), L={L:.0f}",
                                 line=dict(color="#1565c0", width=2.5)))
        fig.add_trace(go.Scatter(x=K_grid, y=Y_prod2, name=f"Y(K), L={L*1.2:.0f}",
                                 line=dict(color="#2e7d32", width=2, dash="dash")))
        fig.update_layout(title="Y(K,L) — Função de Produção Cobb-Douglas",
                          xaxis_title="Capital (K)",
                          yaxis_title="Produto (Y)",
                          template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
**Equação:** ${eq_prod}$

**Retornos:** Constantes de escala, decrescentes em cada fator.

**Interdependência:**
- A (PTF) determina o **produto potencial Yn**
- Yn alimenta a OA de longo prazo e o hiato do produto
- {"**Clássico:** PMgK = r e PMgL = w/P determinam demanda por fatores." if escola == "Clássica" else "**Keynesiano:** Capacidade produtiva existe mas pode ficar ociosa (demanda insuficiente)."}
""")# Garante que chaves novas do DEFAULT_PARAMS sejam adicionadas
# mesmo que a sessão já exista com params antigos
from core.parameters import DEFAULT_PARAMS

if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
else:
    # Preenche chaves faltantes sem sobrescrever as existentes
    for key, val in DEFAULT_PARAMS.items():
        if key not in st.session_state.params:
            st.session_state.params[key] = val
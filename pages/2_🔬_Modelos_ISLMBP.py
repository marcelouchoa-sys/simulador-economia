import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.parameters import DEFAULT_PARAMS
from models.islm import solve_islm, curva_is, curva_lm   # ← CORRETO

st.set_page_config(layout="wide")

# ── ESTADO GLOBAL ─────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",
        "color_base":  "#1565c0",
        "color_shock": "#c62828",
        "color_final": "#2e7d32",
        "show_grid":   True
    }

p      = st.session_state.params
c_base  = st.session_state.settings["color_base"]
c_shock = st.session_state.settings["color_shock"]
nivel   = st.session_state.settings["nivel"]

# ── BOTÃO EXECUTAR ────────────────────────────
with st.sidebar:
    st.divider()
    run = st.button("🚀 Executar Simulação", use_container_width=True)

# ── TÍTULO ────────────────────────────────────
st.title("📉 Modelo IS-LM")

if nivel == "Avançado":
    st.latex(r"Y^* = \frac{\text{mult} \cdot A \cdot h + \text{mult} \cdot b \cdot M/P}{h + \text{mult} \cdot b \cdot k}")
    st.latex(r"r^* = \frac{k \cdot Y^* - M/P}{h}")
elif nivel == "Médio":
    st.caption("Equilíbrio simultâneo entre mercado de bens (IS) e monetário (LM).")
else:
    st.info("📊 IS-LM mostra como juros e renda se determinam conjuntamente na economia.")

# ── CONTROLES ────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    G = st.slider("Gasto do Governo (G)", 0.0, 1000.0, float(p["G"]), 10.0)
    T = st.slider("Impostos (T)",         0.0, 1000.0, float(p["T"]), 10.0)

with col2:
    M = st.slider("Oferta Monetária (M)", 100.0, 3000.0, float(p["M"]), 50.0)
    P = st.slider("Nível de Preços (P)",  0.5,   5.0,    float(p["P"]), 0.1)

if run:
    p["G"] = G
    p["T"] = T
    p["M"] = M
    p["P"] = P

# ── EQUILÍBRIO ───────────────────────────────
eq = solve_islm(p["c0"], p["c1"], p["T"], p["I0"], p["b"],
                p["G"],  p["k"],  p["h"], p["M"],  p["P"])

# ── CURVAS ───────────────────────────────────
Y_grid = np.linspace(100, 2000, 400)

IS = curva_is(Y_grid, p["c0"], p["c1"], p["T"],
              p["I0"], p["b"], p["G"])
LM = curva_lm(Y_grid, p["k"], p["h"], p["M"], p["P"])

# ── GRÁFICO ──────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=Y_grid, y=IS,
    name="IS",
    line=dict(color=c_base, width=3)
))

fig.add_trace(go.Scatter(
    x=Y_grid, y=LM,
    name="LM",
    line=dict(color=c_shock, width=3)
))

fig.add_trace(go.Scatter(
    x=[eq["Y"]], y=[eq["r"]],
    mode="markers+text",
    marker=dict(size=14, color="black", symbol="star"),
    text=["E*"],
    textposition="top right",
    name="Equilíbrio"
))

fig.update_layout(
    title="Equilíbrio IS-LM",
    xaxis_title="Produto (Y)",
    yaxis_title="Taxa de Juros (r)",
    template="plotly_white",
    height=500,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# ── RESULTADOS ───────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Y*",           f"{eq['Y']:.2f}")
col2.metric("r*",           f"{eq['r']*100:.2f}%")
col3.metric("Consumo (C)",  f"{eq['C']:.2f}")
col4.metric("Investimento", f"{eq['I']:.2f}")

if nivel in ["Médio", "Avançado"]:
    st.markdown(f"""
    **Multiplicador fiscal:** {eq['mult']:.3f}  
    **Demanda autônoma (A):** {eq['A']:.2f}  
    **Poupança (S):** {eq['S']:.2f}
    """)
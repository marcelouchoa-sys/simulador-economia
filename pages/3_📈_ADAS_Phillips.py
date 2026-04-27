import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.parameters import DEFAULT_PARAMS
from models.adas import solve_adas, curva_da, curva_oa_cp
from models.phillips import solve_phillips, curva_phillips_cp

st.set_page_config(layout="wide")

# ── ESTADO GLOBAL ─────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",
        "color_base": "#1565c0",
        "color_shock": "#c62828",
        "color_final": "#2e7d32",
        "show_grid": True
    }

p = st.session_state.params

# ── SETTINGS ──────────────────────────────────
c_base  = st.session_state.settings["color_base"]
c_shock = st.session_state.settings["color_shock"]
nivel   = st.session_state.settings["nivel"]

# ── BOTÃO EXECUTAR ────────────────────────────
with st.sidebar:
    st.divider()
    run = st.button("🚀 Executar Simulação", use_container_width=True)

# ── TÍTULO ────────────────────────────────────
st.title("📈 AD-AS + Curva de Phillips")

# ── EXPLICAÇÃO POR NÍVEL ─────────────────────
if nivel == "Avançado":
    st.latex(r"P = P^e + \frac{Y - Y_n}{\alpha}")
elif nivel == "Médio":
    st.caption("DA vem do IS-LM. OA vem de expectativas e rigidez.")
else:
    st.info("📊 Preços e produção são determinados pela interação entre demanda e oferta.")

# ── CONTROLES ────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    G = st.slider("G", 0.0, 1000.0, float(p["G"]), 10.0)
    M = st.slider("M", 0.0, 2000.0, float(p["M"]), 50.0)

with col2:
    Pe = st.slider("Expectativa de Preços (Pe)", 0.5, 3.0, float(p["Pe"]), 0.1)
    alpha = st.slider("α", 0.1, 10.0, float(p["alpha"]), 0.1)

# ── EXECUÇÃO CONTROLADA ──────────────────────
if run:
    p["G"], p["M"], p["Pe"], p["alpha"] = G, M, Pe, alpha

# ── EQUILÍBRIO ───────────────────────────────
eq = solve_adas(p["c0"], p["c1"], p["T"], p["I0"], p["b"],
                p["G"], p["k"], p["h"], p["M"],
                p["Pe"], p["Yn"], p["alpha"])

ph = solve_phillips(eq["Y"], p["Yn"], p["Pe"], p["alpha"])

# ── CURVAS ───────────────────────────────────
P_grid = np.linspace(0.5, 3, 300)
Y_grid = np.linspace(200, 2000, 300)
u_grid = np.linspace(0.01, 0.15, 300)

Y_da = curva_da(P_grid, p["c0"], p["c1"], p["T"],
                p["I0"], p["b"], p["G"],
                p["k"], p["h"], p["M"])

P_oa = curva_oa_cp(Y_grid, p["Pe"], p["Yn"], p["alpha"])

pi_cp = curva_phillips_cp(u_grid, ph["pi_e"],
                          ph["u_natural"], ph["gamma"])

# ── GRÁFICOS ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=Y_da, y=P_grid,
                              name="DA",
                              line=dict(color=c_base, width=3)))
    fig1.add_trace(go.Scatter(x=Y_grid, y=P_oa,
                              name="OA",
                              line=dict(color=c_shock, width=3)))
    fig1.add_trace(go.Scatter(
        x=[eq["Y"]], y=[eq["P"]],
        mode="markers",
        marker=dict(size=12, color="black")
    ))
    fig1.update_layout(title="AD-AS", template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=u_grid*100, y=pi_cp*100,
        name="Phillips",
        line=dict(color=c_base, width=3)
    ))
    fig2.add_trace(go.Scatter(
        x=[ph["u"]*100], y=[ph["pi"]*100],
        mode="markers",
        marker=dict(size=12, color="red")
    ))
    fig2.update_layout(title="Curva de Phillips",
                       template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

# ── RESULTADOS ───────────────────────────────
st.markdown(f"""
### Resultados

- **Produto (Y)**: {eq['Y']:.2f}
- **Preços (P)**: {eq['P']:.4f}
- **Desemprego (u)**: {ph['u']*100:.2f}%
- **Inflação (π)**: {ph['pi']*100:.2f}%
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
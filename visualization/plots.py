import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.islm import solve_islm


# ============================================================
# Helpers
# ============================================================
def _get_c(p):
    return p.get("c1", p.get("c", 0.8))


def _calc_price(eq, p):
    Yn = p.get("Yn", eq["Y"])
    Pe = p.get("Pe", 1.0)
    alpha = p.get("alpha", 100.0)
    if alpha == 0:
        alpha = 1.0
    return Pe + (eq["Y"] - Yn) / alpha


def _calc_unemployment(eq, p):
    un = p.get("un", 0.05)
    lambda_ = p.get("lambda", 0.5)
    Yn = p.get("Yn", eq["Y"])
    gap = (eq["Y"] - Yn) / Yn if Yn != 0 else 0.0
    return max(0.0, un - lambda_ * gap)


def _calc_inflation(P, Pe):
    return (P / Pe - 1.0) if Pe != 0 else 0.0


def _is_curve(p, y_grid):
    c = _get_c(p)
    b = p.get("b", 50.0)
    c0 = p.get("c0", 100.0)
    I0 = p.get("I0", 150.0)
    G = p.get("G", 200.0)
    T = p.get("T", 100.0)

    if abs(b) < 1e-9:
        b = 1e-9

    A = c0 - c * T + I0 + G
    r_grid = (A - (1 - c) * y_grid) / b
    return y_grid, r_grid


def _lm_curve(p, y_grid, price_level):
    k = p.get("k", 0.5)
    h = p.get("h", 100.0)
    M = p.get("M", 500.0)

    if abs(h) < 1e-9:
        h = 1e-9
    if abs(price_level) < 1e-9:
        price_level = 1e-9

    r_grid = (k * y_grid - M / price_level) / h
    return y_grid, r_grid


def _bp_curve(p, y_grid):
    r_world = p.get("r_world", 0.03)
    kf = p.get("kf", 50.0)
    m = p.get("m", 0.2)

    if abs(kf) < 1e-9:
        kf = 1e-9

    r_grid = r_world + (m / kf) * y_grid
    return y_grid, r_grid


def _ad_curve(p, p_grid):
    c = _get_c(p)
    b = p.get("b", 50.0)
    k = p.get("k", 0.5)
    h = p.get("h", 100.0)
    M = p.get("M", 500.0)
    c0 = p.get("c0", 100.0)
    I0 = p.get("I0", 150.0)
    G = p.get("G", 200.0)
    T = p.get("T", 100.0)

    A = c0 - c * T + I0 + G
    mult = 1.0 / max(1e-9, (1 - c))
    denom = 1.0 + mult * b * k / max(h, 1e-9)

    y_vals = []
    for P in p_grid:
        P_eff = max(P, 1e-9)
        y = (mult * A + mult * b * M / (h * P_eff)) / denom
        y_vals.append(y)

    return np.array(y_vals), p_grid


def _as_curve(p, y_grid):
    Pe = p.get("Pe", 1.0)
    Yn = p.get("Yn", 1000.0)
    alpha = p.get("alpha", 100.0)

    if abs(alpha) < 1e-9:
        alpha = 1e-9

    p_grid = Pe + (y_grid - Yn) / alpha
    return y_grid, p_grid


def _phillips_curve(p, u_grid):
    un = p.get("un", 0.05)
    beta = p.get("beta", 1.0)
    pi_e = p.get("pi_e", 0.02)

    pi_grid = pi_e - beta * (u_grid - un)
    return u_grid, pi_grid


def _add_equilibrium_guides(fig, x, y, row, col, color, showlegend=False, name="Equilíbrio"):
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(size=10, color=color, line=dict(color="white", width=1)),
            name=name,
            showlegend=showlegend,
        ),
        row=row,
        col=col,
    )

    fig.add_hline(
        y=y,
        line=dict(color=color, width=1, dash="dot"),
        row=row,
        col=col,
    )
    fig.add_vline(
        x=x,
        line=dict(color=color, width=1, dash="dot"),
        row=row,
        col=col,
    )


def _add_arrow(fig, x0, y0, x1, y1, row, col, color):
    fig.add_annotation(
        x=x1,
        y=y1,
        ax=x0,
        ay=y0,
        xref=f"x{'' if (row, col) == (1, 1) else (col + (row - 1) * 3)}",
        yref=f"y{'' if (row, col) == (1, 1) else (col + (row - 1) * 3)}",
        axref=f"x{'' if (row, col) == (1, 1) else (col + (row - 1) * 3)}",
        ayref=f"y{'' if (row, col) == (1, 1) else (col + (row - 1) * 3)}",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor=color,
    )


# ============================================================
# Principal
# ============================================================
def build_comparison_dashboard(
    p_base,
    p_shock,
    show_bp=True,
    show_arrows=True,
    show_grid=True,
    color_base="#1565c0",
    color_shock="#c62828",
    color_bp="#2e7d32",
    line_width=2,
    show_islm=True,
    show_adas=True,
    show_phillips=True,
    bp_b=None,
    bp_s=None,
):
    eq_b = solve_islm(p_base)
    eq_s = solve_islm(p_shock)

    P_b = _calc_price(eq_b, p_base)
    P_s = _calc_price(eq_s, p_shock)

    u_b = _calc_unemployment(eq_b, p_base)
    u_s = _calc_unemployment(eq_s, p_shock)

    pi_b = _calc_inflation(P_b, p_base.get("Pe", 1.0))
    pi_s = _calc_inflation(P_s, p_shock.get("Pe", 1.0))

    y_min = max(1.0, min(eq_b["Y"], eq_s["Y"]) * 0.6)
    y_max = max(eq_b["Y"], eq_s["Y"]) * 1.4
    y_grid = np.linspace(y_min, y_max, 250)

    r_candidates = [eq_b["r"], eq_s["r"]]
    p_max_guess = max(P_b, P_s, 1.5)
    p_min_guess = max(0.05, min(P_b, P_s, 1.0) * 0.5)
    p_grid = np.linspace(p_min_guess, p_max_guess * 1.8, 250)

    u_min = max(0.0, min(u_b, u_s, 0.02) * 0.5)
    u_max = max(u_b, u_s, 0.12) * 1.4
    u_grid = np.linspace(u_min, u_max, 250)

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("IS-LM-BP", "AD-AS", "Curva de Phillips"),
        horizontal_spacing=0.08,
    )

    # ========================================================
    # 1) IS-LM-BP
    # ========================================================
    if show_islm:
        y_is_b, r_is_b = _is_curve(p_base, y_grid)
        y_is_s, r_is_s = _is_curve(p_shock, y_grid)
        y_lm_b, r_lm_b = _lm_curve(p_base, y_grid, P_b)
        y_lm_s, r_lm_s = _lm_curve(p_shock, y_grid, P_s)

        fig.add_trace(
            go.Scatter(
                x=y_is_b,
                y=r_is_b,
                mode="lines",
                line=dict(color=color_base, width=line_width, dash="solid"),
                name="IS Base",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=y_lm_b,
                y=r_lm_b,
                mode="lines",
                line=dict(color=color_base, width=line_width, dash="dot"),
                name="LM Base",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=y_is_s,
                y=r_is_s,
                mode="lines",
                line=dict(color=color_shock, width=line_width, dash="solid"),
                name="IS Choque",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=y_lm_s,
                y=r_lm_s,
                mode="lines",
                line=dict(color=color_shock, width=line_width, dash="dot"),
                name="LM Choque",
            ),
            row=1,
            col=1,
        )

        if show_bp:
            y_bp_b, r_bp_b = _bp_curve(p_base, y_grid)
            r_candidates.extend([float(np.min(r_bp_b)), float(np.max(r_bp_b))])

            fig.add_trace(
                go.Scatter(
                    x=y_bp_b,
                    y=r_bp_b,
                    mode="lines",
                    line=dict(color=color_bp, width=line_width, dash="dash"),
                    name="BP Base",
                ),
                row=1,
                col=1,
            )

            kf_b = p_base.get("kf", 50.0)
            r_world_b = p_base.get("r_world", 0.03)
            m_b = p_base.get("m", 0.2)

            same_bp = (
                abs(kf_b - p_shock.get("kf", 50.0)) < 1e-9
                and abs(r_world_b - p_shock.get("r_world", 0.03)) < 1e-9
                and abs(m_b - p_shock.get("m", 0.2)) < 1e-9
            )

            if not same_bp:
                y_bp_s, r_bp_s = _bp_curve(p_shock, y_grid)
                r_candidates.extend([float(np.min(r_bp_s)), float(np.max(r_bp_s))])

                fig.add_trace(
                    go.Scatter(
                        x=y_bp_s,
                        y=r_bp_s,
                        mode="lines",
                        line=dict(color=color_bp, width=line_width, dash="longdash"),
                        name="BP Choque",
                    ),
                    row=1,
                    col=1,
                )

        _add_equilibrium_guides(fig, eq_b["Y"], eq_b["r"], 1, 1, color_base, True, "Equilíbrio Base")
        _add_equilibrium_guides(fig, eq_s["Y"], eq_s["r"], 1, 1, color_shock, True, "Equilíbrio Choque")

        if show_arrows:
            _add_arrow(fig, eq_b["Y"], eq_b["r"], eq_s["Y"], eq_s["r"], 1, 1, "#2e7d32")

        if bp_b is not None:
            fig.add_annotation(
                x=eq_b["Y"],
                y=eq_b["r"],
                text=f"BP₀={bp_b:+.2f}",
                showarrow=False,
                font=dict(color=color_base, size=11),
                yshift=18,
                row=1,
                col=1,
            )
        if bp_s is not None:
            fig.add_annotation(
                x=eq_s["Y"],
                y=eq_s["r"],
                text=f"BP₁={bp_s:+.2f}",
                showarrow=False,
                font=dict(color=color_shock, size=11),
                yshift=-18,
                row=1,
                col=1,
            )
    else:
        fig.add_annotation(
            text="IS-LM oculto",
            x=0.16,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16),
        )

    # ========================================================
    # 2) AD-AS
    # ========================================================
    if show_adas:
        y_ad_b, p_ad_b = _ad_curve(p_base, p_grid)
        y_ad_s, p_ad_s = _ad_curve(p_shock, p_grid)

        y_as_b, p_as_b = _as_curve(p_base, y_grid)
        y_as_s, p_as_s = _as_curve(p_shock, y_grid)

        fig.add_trace(
            go.Scatter(
                x=y_ad_b,
                y=p_ad_b,
                mode="lines",
                line=dict(color=color_base, width=line_width, dash="solid"),
                name="AD Base",
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=y_as_b,
                y=p_as_b,
                mode="lines",
                line=dict(color=color_base, width=line_width, dash="dot"),
                name="AS Base",
            ),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=y_ad_s,
                y=p_ad_s,
                mode="lines",
                line=dict(color=color_shock, width=line_width, dash="solid"),
                name="AD Choque",
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=y_as_s,
                y=p_as_s,
                mode="lines",
                line=dict(color=color_shock, width=line_width, dash="dot"),
                name="AS Choque",
            ),
            row=1,
            col=2,
        )

        _add_equilibrium_guides(fig, eq_b["Y"], P_b, 1, 2, color_base, False, "Eq. AD-AS Base")
        _add_equilibrium_guides(fig, eq_s["Y"], P_s, 1, 2, color_shock, False, "Eq. AD-AS Choque")

        if show_arrows:
            _add_arrow(fig, eq_b["Y"], P_b, eq_s["Y"], P_s, 1, 2, "#2e7d32")
    else:
        fig.add_annotation(
            text="AD-AS oculto",
            x=0.50,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16),
        )

    # ========================================================
    # 3) Phillips
    # ========================================================
    if show_phillips:
        u_pc_b, pi_pc_b = _phillips_curve(p_base, u_grid)
        u_pc_s, pi_pc_s = _phillips_curve(p_shock, u_grid)

        fig.add_trace(
            go.Scatter(
                x=u_pc_b * 100,
                y=pi_pc_b * 100,
                mode="lines",
                line=dict(color=color_base, width=line_width, dash="solid"),
                name="Phillips Base",
            ),
            row=1,
            col=3,
        )
        fig.add_trace(
            go.Scatter(
                x=u_pc_s * 100,
                y=pi_pc_s * 100,
                mode="lines",
                line=dict(color=color_shock, width=line_width, dash="solid"),
                name="Phillips Choque",
            ),
            row=1,
            col=3,
        )

        _add_equilibrium_guides(fig, u_b * 100, pi_b * 100, 1, 3, color_base, False, "Eq. Phillips Base")
        _add_equilibrium_guides(fig, u_s * 100, pi_s * 100, 1, 3, color_shock, False, "Eq. Phillips Choque")

        if show_arrows:
            _add_arrow(fig, u_b * 100, pi_b * 100, u_s * 100, pi_s * 100, 1, 3, "#2e7d32")
    else:
        fig.add_annotation(
            text="Phillips oculto",
            x=0.84,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16),
        )

    # ========================================================
    # Layout final
    # ========================================================
    r_min = min(r_candidates) if r_candidates else -0.05
    r_max = max(r_candidates) if r_candidates else 0.20
    r_pad = max(0.02, (r_max - r_min) * 0.15)

    fig.update_xaxes(title_text="Y (Produto)", row=1, col=1, showgrid=show_grid)
    fig.update_yaxes(title_text="r (Juros)", row=1, col=1, showgrid=show_grid, range=[r_min - r_pad, r_max + r_pad])

    fig.update_xaxes(title_text="Y (Produto)", row=1, col=2, showgrid=show_grid)
    fig.update_yaxes(title_text="P (Preços)", row=1, col=2, showgrid=show_grid)

    fig.update_xaxes(title_text="u (Desemprego, %)", row=1, col=3, showgrid=show_grid)
    fig.update_yaxes(title_text="π (Inflação, %)", row=1, col=3, showgrid=show_grid)

    fig.update_layout(
        height=650,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=30, r=30, t=90, b=30),
        title=dict(
            text="Painel Comparativo: IS-LM-BP | AD-AS | Curva de Phillips",
            x=0.5,
        ),
    )

    return fig
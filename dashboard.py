"""
dashboard.py — AI Validation Confidence Monitor
Run: streamlit run dashboard.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import locate_csv, load_and_validate
from metrics import compute_all_metrics, generate_executive_summary

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Validation Confidence Monitor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Premium Dark Design
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Base ─────────────────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    background-color: #050b18 !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%) !important;
    border-right: 1px solid rgba(99,137,255,0.15) !important;
}

/* ── Main area padding ─────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1400px;
}

/* ── Widget labels (selectbox, checkbox, radio, etc.) ─── */
label, .stSelectbox label, .stCheckbox label,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
.stSelectbox > label, .stCheckbox > label,
div[data-testid="stCheckbox"] label,
div[data-testid="stSelectbox"] label,
.stRadio label,
p[data-testid="stWidgetLabel"] {
    color: #c8d8ff !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* ── Selectbox box ────────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    background-color: #0d1f3c !important;
    border: 1px solid rgba(99,137,255,0.25) !important;
    border-radius: 8px !important;
    color: #c8d8ff !important;
}
div[data-testid="stSelectbox"] > div > div > div {
    color: #c8d8ff !important;
}

/* ── Checkbox — target every possible structure ───────── */
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label div,
div[data-testid="stCheckbox"] > div > label,
div[data-testid="stCheckbox"] span:not([data-baseweb]),
div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"],
div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] span {
    color: #c8d8ff !important;
    font-weight: 600 !important;
}

/* ── Custom filter label (manual markdown labels) ─────── */
.filter-lbl {
    color: #c8d8ff !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin-bottom: 4px;
    letter-spacing: 0.2px;
    display: block;
}

/* ── All text inside stMarkdown / widgets ─────────────── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
.stMarkdown p {
    color: #c8d8ff;
}

/* ══════════════════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════════════════ */
.hero-wrapper {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a1628 50%, #0d1f3c 100%);
    border: 1px solid rgba(99,137,255,0.2);
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(99,137,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -40px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(0,210,230,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #ffffff 0%, #a8c4ff 60%, #6389ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 6px 0;
    line-height: 1.1;
}
.hero-sub {
    font-size: 14px;
    color: #8fa8cc;
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.3px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 24px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    border: 1.5px solid;
}
.badge-critical   { border-color: #ff4b4b; color: #ff4b4b; background: rgba(255,75,75,0.08); }
.badge-high       { border-color: #ff8800; color: #ff8800; background: rgba(255,136,0,0.08); }
.badge-governance { border-color: #ff0055; color: #ff0055; background: rgba(255,0,85,0.08); }
.badge-elevated   { border-color: #ffd600; color: #ffd600; background: rgba(255,214,0,0.08); }
.badge-ok         { border-color: #00d97e; color: #00d97e; background: rgba(0,217,126,0.08); }

/* ══════════════════════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════════════════════ */
.section-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 36px 0 18px 0;
}
.section-line {
    height: 2px;
    flex: 1;
    background: linear-gradient(90deg, rgba(99,137,255,0.4) 0%, transparent 100%);
    border-radius: 2px;
}
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #6389ff;
    white-space: nowrap;
}
.section-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #6389ff;
    box-shadow: 0 0 8px rgba(99,137,255,0.8);
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════════
   KPI CARDS
══════════════════════════════════════════════════════════ */
.kpi-outer {
    background: linear-gradient(135deg, #0d1f3c, #0a1628);
    border-radius: 16px;
    padding: 2px;
    height: 100%;
    transition: transform 0.2s;
}
.kpi-inner {
    background: #080f1e;
    border-radius: 14px;
    padding: 22px 18px 18px 18px;
    text-align: center;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.kpi-inner::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 14px 14px;
}
.kpi-glow-blue::after   { background: linear-gradient(90deg, transparent, #6389ff, transparent); }
.kpi-glow-green::after  { background: linear-gradient(90deg, transparent, #00d97e, transparent); }
.kpi-glow-red::after    { background: linear-gradient(90deg, transparent, #ff4b4b, transparent); }
.kpi-glow-yellow::after { background: linear-gradient(90deg, transparent, #ffd600, transparent); }
.kpi-glow-orange::after { background: linear-gradient(90deg, transparent, #ff8800, transparent); }

.kpi-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
}
.kpi-label {
    font-size: 10px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #7a90b8;
    margin-bottom: 10px;
    font-weight: 600;
}
.kpi-value {
    font-size: 34px;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: -1px;
}
.kpi-sub {
    font-size: 11px;
    color: #6b7fa8;
    font-weight: 500;
}

/* ══════════════════════════════════════════════════════════
   EXEC SUMMARY
══════════════════════════════════════════════════════════ */
.exec-box {
    background: linear-gradient(135deg, #080f1e 0%, #0a1628 100%);
    border: 1px solid rgba(99,137,255,0.2);
    border-left: 3px solid #6389ff;
    border-radius: 16px;
    padding: 28px 32px;
    font-size: 14px;
    line-height: 2;
    color: #8fa3cc;
    white-space: pre-wrap;
    position: relative;
}
.exec-box::before {
    content: '"';
    font-size: 80px;
    color: rgba(99,137,255,0.08);
    position: absolute;
    top: -10px;
    left: 20px;
    line-height: 1;
    font-family: Georgia, serif;
}

/* ══════════════════════════════════════════════════════════
   PHASE CARDS
══════════════════════════════════════════════════════════ */
.phase-card {
    background: linear-gradient(135deg, #080f1e, #0a1628);
    border: 1px solid rgba(99,137,255,0.15);
    border-radius: 16px;
    padding: 22px;
    height: 100%;
}
.phase-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 800;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(99,137,255,0.1);
}
.mrow {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 13px;
}
.mrow:last-child { border-bottom: none; }
.mrow-name { color: #8892b0; font-weight: 500; }
.mrow-val  { font-weight: 700; color: #c8d8ff; }

/* ══════════════════════════════════════════════════════════
   RISK SIGNALS
══════════════════════════════════════════════════════════ */
.risk-overall-card {
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.risk-signal-card {
    background: #080f1e;
    border: 1px solid rgba(99,137,255,0.1);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
}
.sig-badge {
    font-size: 10px;
    font-weight: 800;
    border-radius: 8px;
    padding: 5px 12px;
    white-space: nowrap;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    min-width: 110px;
    text-align: center;
    flex-shrink: 0;
}
.sig-critical   { background: rgba(255,75,75,0.15);  color: #ff4b4b;  border: 1px solid rgba(255,75,75,0.3); }
.sig-high       { background: rgba(255,136,0,0.15);  color: #ff8800;  border: 1px solid rgba(255,136,0,0.3); }
.sig-governance { background: rgba(255,0,85,0.15);   color: #ff0055;  border: 1px solid rgba(255,0,85,0.3); }
.sig-elevated   { background: rgba(255,214,0,0.15);  color: #ffd600;  border: 1px solid rgba(255,214,0,0.3); }
.sig-ok         { background: rgba(0,217,126,0.15);  color: #00d97e;  border: 1px solid rgba(0,217,126,0.3); }
.sig-name  { font-weight: 700; color: #c8d8ff; font-size: 14px; }
.sig-val   { color: #7a90b8; font-size: 12px; margin-left: 8px; }
.sig-desc  { color: #7a90b8; font-size: 12px; margin-top: 4px; line-height: 1.6; }

/* ══════════════════════════════════════════════════════════
   SIDEBAR METRICS
══════════════════════════════════════════════════════════ */
.sb-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid rgba(99,137,255,0.07);
}
.sb-label { color: #8892b0; font-size: 12px; font-weight: 500; }
.sb-val   { font-size: 13px; font-weight: 800; }

/* ══════════════════════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════════════════════ */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,137,255,0.3), transparent);
    margin: 8px 0;
    border: none;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA + METRICS (cached)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Loading telemetry…")
def load_data():
    filepath = locate_csv()
    return load_and_validate(filepath)


@st.cache_data(show_spinner="Computing metrics…")
def get_metrics(_df: pd.DataFrame):
    return compute_all_metrics(_df)


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

SEV_COLOR = {
    "Critical": "#ff4b4b",
    "High Risk": "#ff8800",
    "Governance Failure": "#ff0055",
    "Elevated": "#ffd600",
    "Acceptable": "#00d97e",
}
SEV_BADGE = {
    "Critical": "badge-critical",
    "High Risk": "badge-high",
    "Governance Failure": "badge-governance",
    "Elevated": "badge-elevated",
    "Acceptable": "badge-ok",
}
SIG_CLASS = {
    "Critical": "sig-critical",
    "High Risk": "sig-high",
    "Governance Failure": "sig-governance",
    "Elevated": "sig-elevated",
    "Acceptable": "sig-ok",
}
ENV_COLOR = {
    "Desktop": "#6389ff",
    "Mobile": "#00d97e",
    "AMP": "#ffd600",
    "AdBlock": "#ff8800",
    "SlowNetwork": "#ff4b4b",
}

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#8fa3cc", size=12),
    margin=dict(l=10, r=10, t=44, b=10),
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: CSS color scale (no matplotlib)
# ═══════════════════════════════════════════════════════════════════════════════

def _color_scale(val, lo, hi, reverse=False):
    """Return a CSS background-color style based on position in [lo, hi]."""
    if pd.isna(val) or hi == lo:
        return ""
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    if reverse:
        t = 1 - t
    # Red (#c0392b) → Yellow (#f39c12) → Green (#1abc9c)
    if t < 0.5:
        s = t * 2
        r = int(192 + (243 - 192) * s)
        g = int(57  + (156 - 57 ) * s)
        b = int(43  + (18  - 43 ) * s)
    else:
        s = (t - 0.5) * 2
        r = int(243 + (26  - 243) * s)
        g = int(156 + (188 - 156) * s)
        b = int(18  + (156 - 18 ) * s)
    return f"background-color: rgba({r},{g},{b},0.25); color: #e0eaff;"


def style_env_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply color scale to FNR and Precision columns without matplotlib."""
    fnr_col = "False Negative Rate (%)"
    prec_col = "Precision (%)"
    fnr_lo, fnr_hi = df[fnr_col].min(), df[fnr_col].max()
    prec_lo, prec_hi = df[prec_col].min(), df[prec_col].max()

    def style_row(row):
        styles = [""] * len(row)
        cols = row.index.tolist()
        if fnr_col in cols:
            i = cols.index(fnr_col)
            styles[i] = _color_scale(row[fnr_col], fnr_lo, fnr_hi, reverse=True)
        if prec_col in cols:
            i = cols.index(prec_col)
            styles[i] = _color_scale(row[prec_col], prec_lo, prec_hi)
        return styles

    return (
        df.style
        .apply(style_row, axis=1)
        .format({
            "Avg Confidence": "{:.1f}",
            fnr_col: "{:.1f}%",
            prec_col: "{:.1f}%",
            "Uncertainty Rate (%)": "{:.1f}%",
            "Avg Latency (ms)": "{:.0f}",
        })
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert #rrggbb hex to rgba(r,g,b,alpha) string safe for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def gauge_chart(value: float, title: str,
                max_val: float = 100,
                thresholds: list[tuple[float, str]] | None = None,
                suffix: str = "%") -> go.Figure:
    steps = []
    if thresholds:
        prev = 0
        for thresh, color in thresholds:
            steps.append({"range": [prev, thresh], "color": _hex_to_rgba(color, 0.18)})
            prev = thresh
        steps.append({"range": [prev, max_val], "color": _hex_to_rgba(thresholds[-1][1], 0.18)})

    bar_color = "#6389ff"
    if thresholds:
        for thresh, c in thresholds:
            if value <= thresh:
                bar_color = c
                break

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={
            "suffix": suffix,
            "font": {"size": 30, "color": bar_color, "family": "Inter"},
            "valueformat": ".1f",
        },
        title={"text": title, "font": {"size": 11, "color": "#6b7fa8"}},
        gauge={
            "axis": {
                "range": [0, max_val],
                "tickcolor": "#2a4060",
                "tickfont": {"color": "#6b7fa8", "size": 9},
                "tickwidth": 1,
            },
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": "rgba(8,15,30,0)",
            "borderwidth": 0,
            "steps": steps or [{"range": [0, max_val], "color": "rgba(10,22,40,0.5)"}],
        },
    ))
    fig.update_layout(**CHART_BASE, height=220)
    return fig


def fnr_trend_chart(df: pd.DataFrame) -> go.Figure:
    df_ts = df.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()
    fig = go.Figure()
    colors = {"Before": "#ff8800", "After": "#00d97e"}
    fills  = {"Before": "rgba(255,136,0,0.07)", "After": "rgba(0,217,126,0.07)"}

    for phase in ["Before", "After"]:
        sub = df_ts[df_ts["phase"] == phase]
        if sub.empty:
            continue
        daily = sub.resample("D").agg(
            fn=("false_negative", "sum"),
            af=("actual_failure", "sum"),
        ).reset_index()
        daily["fnr"] = (daily["fn"] / daily["af"].replace(0, np.nan)) * 100
        daily["fnr"] = daily["fnr"].fillna(0).rolling(7, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=daily["timestamp"], y=daily["fnr"],
            name=f"{phase}", mode="lines",
            line=dict(color=colors[phase], width=2.5, shape="spline"),
            fill="tozeroy", fillcolor=fills[phase],
        ))

    fig.add_hline(y=10, line_dash="dot", line_color="rgba(255,75,75,0.5)",
                  annotation_text="Critical 10%",
                  annotation_font=dict(color="#ff4b4b", size=10))
    fig.add_hline(y=5, line_dash="dot", line_color="rgba(255,214,0,0.4)",
                  annotation_text="Elevated 5%",
                  annotation_font=dict(color="#ffd600", size=10))
    fig.update_layout(
        **CHART_BASE,
        title=dict(text="False Negative Rate — 7-Day Rolling", font=dict(size=13, color="#6b7fa8")),
        xaxis=dict(showgrid=False, color="#6b7fa8", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1a2d4a", color="#6b7fa8",
                   title="FNR (%)", zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=320,
    )
    return fig


def env_bar_chart(env_df: pd.DataFrame) -> go.Figure:
    colors = [ENV_COLOR.get(e, "#6389ff") for e in env_df["Environment"]]
    fig = go.Figure(go.Bar(
        y=env_df["Environment"],
        x=env_df["False Negative Rate (%)"],
        orientation="h",
        marker=dict(
            color=[_hex_to_rgba(c, 0.8) for c in colors],
            line=dict(color=colors, width=1.5),
        ),
        text=env_df["False Negative Rate (%)"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        textfont=dict(color="#8fa3cc", size=12, family="Inter"),
    ))
    fig.add_vline(x=10, line_dash="dot",
                  line_color="rgba(255,75,75,0.5)",
                  annotation_text="Critical",
                  annotation_font=dict(color="#ff4b4b", size=10))
    fig.update_layout(
        **CHART_BASE,
        title=dict(text="False Negative Rate by Environment", font=dict(size=13, color="#6b7fa8")),
        xaxis=dict(showgrid=True, gridcolor="#1a2d4a", color="#6b7fa8", title="FNR (%)"),
        yaxis=dict(showgrid=False, color="#8fa3cc"),
        height=280,
    )
    return fig


def conf_vs_prec_chart(df: pd.DataFrame) -> go.Figure:
    from metrics import compute_precision
    fig = go.Figure()
    for env in sorted(df["environment"].dropna().unique()):
        sub = df[df["environment"] == env]
        prec = compute_precision(sub) * 100
        conf = sub["ai_confidence_score"].mean()
        c = ENV_COLOR.get(env, "#6389ff")
        fig.add_trace(go.Scatter(
            x=[conf], y=[prec],
            mode="markers+text",
            name=env,
            text=[env],
            textposition="top center",
            textfont=dict(size=11, color="#8fa3cc"),
            marker=dict(
                size=max(16, len(sub) / 8),
                color=_hex_to_rgba(c, 0.6),
                line=dict(width=2, color=c),
            ),
        ))
    # diagonal
    fig.add_shape(type="line", x0=78, y0=78, x1=102, y1=102,
                  line=dict(color="#1a2a50", dash="dot", width=1.5))
    fig.add_annotation(x=98, y=99, text="Ideal alignment",
                       showarrow=False, font=dict(size=9, color="#6b7fa8"))
    fig.update_layout(
        **CHART_BASE,
        title=dict(text="Confidence vs Precision by Environment", font=dict(size=13, color="#6b7fa8")),
        xaxis=dict(title="Avg AI Confidence (%)", showgrid=True,
                   gridcolor="#1a2d4a", color="#6b7fa8"),
        yaxis=dict(title="Precision (%)", showgrid=True,
                   gridcolor="#1a2d4a", color="#6b7fa8"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=280,
    )
    return fig


def before_after_chart(before: dict, after: dict) -> go.Figure:
    keys = {
        "ECS": "ecs",
        "FN Rate": "false_negative_rate",
        "Conf Gap": "confidence_gap",
        "RAI": "rai",
        "Precision": "precision",
    }
    labels = list(keys.keys())
    bv = [before.get(v) or 0 for v in keys.values()]
    av = [after.get(v)  or 0 for v in keys.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Before", x=labels, y=bv,
        marker=dict(color="rgba(255,136,0,0.7)", line=dict(color="#ff8800", width=1.5)),
        text=[f"{v:.1f}" for v in bv], textposition="outside",
        textfont=dict(size=11, color="#8fa3cc"),
    ))
    fig.add_trace(go.Bar(
        name="After", x=labels, y=av,
        marker=dict(color="rgba(0,217,126,0.7)", line=dict(color="#00d97e", width=1.5)),
        text=[f"{v:.1f}" for v in av], textposition="outside",
        textfont=dict(size=11, color="#8fa3cc"),
    ))
    fig.update_layout(
        **CHART_BASE,
        title=dict(text="Before vs After — Key Metrics", font=dict(size=13, color="#6b7fa8")),
        barmode="group",
        xaxis=dict(showgrid=False, color="#8fa3cc"),
        yaxis=dict(showgrid=True, gridcolor="#1a2d4a", color="#6b7fa8"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=320,
    )
    return fig


def uncertainty_trend_chart(df: pd.DataFrame) -> go.Figure:
    df_ts = df.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()
    fig = go.Figure()
    colors = {"Before": "#ff8800", "After": "#6389ff"}
    fills  = {"Before": "rgba(255,136,0,0.07)", "After": "rgba(99,137,255,0.07)"}

    for phase in ["Before", "After"]:
        sub = df_ts[df_ts["phase"] == phase]
        if sub.empty:
            continue
        daily = sub.resample("D").agg(
            unc=("uncertainty_flag", "sum"),
            tot=("uncertainty_flag", "count"),
        ).reset_index()
        daily["rate"] = (daily["unc"] / daily["tot"].replace(0, np.nan)) * 100
        daily["rate"] = daily["rate"].fillna(0).rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=daily["timestamp"], y=daily["rate"],
            name=f"{phase}", mode="lines",
            line=dict(color=colors[phase], width=2.5, shape="spline"),
            fill="tozeroy", fillcolor=fills[phase],
        ))
    fig.update_layout(
        **CHART_BASE,
        title=dict(text="Uncertainty Rate — 7-Day Rolling", font=dict(size=13, color="#6b7fa8")),
        xaxis=dict(showgrid=False, color="#6b7fa8", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1a2d4a", color="#6b7fa8",
                   title="Uncertainty (%)", zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=320,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def section(label: str):
    st.markdown(
        f"<div class='section-wrap'>"
        f"<div class='section-dot'></div>"
        f"<span class='section-label'>{label}</span>"
        f"<div class='section-line'></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str, icon: str, glow: str):
    st.markdown(
        f"<div class='kpi-outer' style='background:linear-gradient(135deg,#0d1f3c,#0a1628);'>"
        f"<div class='kpi-inner kpi-glow-{glow}'>"
        f"<span class='kpi-icon'>{icon}</span>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value' style='color:{_glow_color(glow)};'>{value}</div>"
        f"<div class='kpi-sub'>{sub}</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _glow_color(g: str) -> str:
    return {"blue":"#6389ff","green":"#00d97e","red":"#ff4b4b",
            "yellow":"#ffd600","orange":"#ff8800"}.get(g,"#6389ff")


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER SECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header(severity: str):
    sc = SEV_COLOR.get(severity, "#6389ff")
    bc = SEV_BADGE.get(severity, "badge-ok")
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(
            f"<div class='hero-wrapper'>"
            f"<h1 class='hero-title'>AI Validation Confidence Monitor</h1>"
            f"<p class='hero-sub'>Real-time governance telemetry · Environment coverage · False negative analysis</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding-top:40px; text-align:right;'>"
            f"<div class='hero-badge {bc}'>⬤ &nbsp;{severity}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_executive_snapshot(metrics: dict):
    section("Executive Snapshot")
    summary = generate_executive_summary(metrics)
    st.markdown(f"<div class='exec-box'>{summary}</div>", unsafe_allow_html=True)


def render_kpis(m: dict):
    section("Governance KPIs")
    aci, ecs, fnr, prec, gap, rai, unc = (
        m["ai_confidence_index"], m["ecs"], m["false_negative_rate"],
        m["precision"], m["confidence_gap"], m["rai"], m["uncertainty_rate"],
    )
    cols = st.columns(7)
    defs = [
        ("AI Confidence",    f"{aci:.1f}%",  "mean score",       "🧠",
         "blue" if aci >= 85 else "orange"),
        ("Coverage (ECS)",   f"{ecs:.0f}%",  "environments",     "🌐",
         "green" if ecs >= 80 else "orange" if ecs >= 60 else "red"),
        ("False Neg. Rate",  f"{fnr:.1f}%",  "missed failures",  "⚠️",
         "green" if fnr <= 5 else "yellow" if fnr <= 10 else "red"),
        ("Precision",        f"{prec:.1f}%", "TP / detected",    "🎯",
         "green" if prec >= 80 else "orange" if prec >= 60 else "red"),
        ("Confidence Gap",   f"{gap:.1f}",   "conf − precision", "📉",
         "green" if gap <= 10 else "yellow" if gap <= 20 else "red"),
        ("RAI",              f"{rai:.1f}",   "reality alignment","🔬",
         "green" if rai >= 70 else "yellow" if rai >= 50 else "red"),
        ("Uncertainty Rate", f"{unc:.1f}%",  "flagged rows",     "🚩",
         "green" if unc <= 10 else "yellow" if unc <= 20 else "red"),
    ]
    for col, (lbl, val, sub, icon, glow) in zip(cols, defs):
        with col:
            kpi_card(lbl, val, sub, icon, glow)


def render_gauges(m: dict):
    section("Confidence Gauges")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(gauge_chart(
            m["ai_confidence_index"], "AI Confidence Index",
            thresholds=[(60,"#ff4b4b"),(80,"#ffd600"),(100,"#00d97e")],
        ), width="stretch")
    with g2:
        st.plotly_chart(gauge_chart(
            m["ecs"], "Environmental Coverage",
            thresholds=[(60,"#ff4b4b"),(80,"#ffd600"),(100,"#00d97e")],
        ), width="stretch")
    with g3:
        st.plotly_chart(gauge_chart(
            m["false_negative_rate"], "False Negative Rate",
            max_val=50,
            thresholds=[(5,"#00d97e"),(10,"#ffd600"),(50,"#ff4b4b")],
        ), width="stretch")
    with g4:
        st.plotly_chart(gauge_chart(
            m["rai"], "Reality Alignment Index",
            thresholds=[(50,"#ff4b4b"),(70,"#ffd600"),(100,"#00d97e")],
            suffix="",
        ), width="stretch")


def render_phase_comparison(before: dict, after: dict):
    section("Before vs After Comparison")
    col_b, col_chart, col_a = st.columns([1, 2, 1])

    def phase_html(data: dict, label: str, color: str) -> str:
        if not data.get("row_count"):
            return f"<div class='phase-card'><p style='color:#7a90b8'>No data</p></div>"
        rows_data = [
            ("Rows",            str(data["row_count"])),
            ("AI Confidence",   f"{data['ai_confidence_index']:.1f}%"),
            ("ECS",             f"{data['ecs']:.0f}%"),
            ("FN Rate",         f"{data['false_negative_rate']:.1f}%"),
            ("Precision",       f"{data['precision']:.1f}%"),
            ("Confidence Gap",  f"{data['confidence_gap']:.1f}"),
            ("RAI",             f"{data['rai']:.1f}"),
            ("Uncertainty",     f"{data['uncertainty_rate']:.1f}%"),
        ]
        rows_html = "".join(
            f"<div class='mrow'>"
            f"<span class='mrow-name'>{n}</span>"
            f"<span class='mrow-val'>{v}</span>"
            f"</div>"
            for n, v in rows_data
        )
        return (
            f"<div class='phase-card'>"
            f"<div class='phase-title' style='color:{color};'>{label}</div>"
            f"{rows_html}"
            f"</div>"
        )

    with col_b:
        st.markdown(phase_html(before, "BEFORE", "#ff8800"), unsafe_allow_html=True)
    with col_chart:
        st.plotly_chart(before_after_chart(before, after), width="stretch")
    with col_a:
        st.markdown(phase_html(after, "AFTER", "#00d97e"), unsafe_allow_html=True)


def render_environment_analysis(env_df: pd.DataFrame, df: pd.DataFrame):
    section("Environment Coverage Analysis")
    col_bar, col_scatter = st.columns(2)
    with col_bar:
        st.plotly_chart(env_bar_chart(env_df), width="stretch")
    with col_scatter:
        st.plotly_chart(conf_vs_prec_chart(df), width="stretch")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.dataframe(
        style_env_table(env_df.copy()),
        width="stretch",
        hide_index=True,
    )


def render_trends(df: pd.DataFrame):
    section("Temporal Trends")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fnr_trend_chart(df), width="stretch")
    with c2:
        st.plotly_chart(uncertainty_trend_chart(df), width="stretch")


def render_risk_signals(risk: dict):
    section("Governance Risk Classification")
    overall = risk["overall_severity"]
    sc = SEV_COLOR.get(overall, "#6389ff")

    st.markdown(
        f"<div class='risk-overall-card' style='"
        f"background:linear-gradient(135deg,{sc}11,{sc}06);"
        f"border:1.5px solid {sc}44;'>"
        f"<div>"
        f"<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
        f"color:#7a90b8;margin-bottom:6px;font-weight:700;'>Overall Governance Risk</div>"
        f"<div style='font-size:28px;font-weight:900;color:{sc};'>{overall}</div>"
        f"</div>"
        f"<div style='font-size:40px;opacity:0.4;'>⬡</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    for sig in risk["signals"]:
        sev = sig["Severity"]
        sc2 = SIG_CLASS.get(sev, "sig-ok")
        st.markdown(
            f"<div class='risk-signal-card'>"
            f"<div class='sig-badge {sc2}'>{sev}</div>"
            f"<div style='flex:1;'>"
            f"<span class='sig-name'>{sig['Signal']}</span>"
            f"<span class='sig-val'>= {sig['Value']:.1f} &nbsp;·&nbsp; threshold {sig['Threshold']}</span>"
            f"<div class='sig-desc'>{sig['Detail']}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_uncertainty_table(df: pd.DataFrame):
    section("Uncertainty Flagged Records")
    flagged = df[df["uncertainty_flag"]].copy()
    pct = len(flagged) / len(df) * 100

    col_stat, _ = st.columns([1, 3])
    with col_stat:
        kpi_card("Flagged Rows", str(len(flagged)), f"{pct:.1f}% of total", "🚩",
                 "green" if pct <= 10 else "yellow" if pct <= 20 else "red")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if flagged.empty:
        st.success("No uncertainty flags in current data.")
        return

    display = flagged[[
        "validation_id","phase","environment","ai_confidence_score",
        "actual_failure","failure_detected_by_ai","false_negative","latency_ms","timestamp",
    ]].sort_values("timestamp").reset_index(drop=True)

    st.dataframe(
        display.style
        .map(lambda v: "color:#ff4b4b;font-weight:700" if v is True else "", subset=["false_negative"])
        .format({"ai_confidence_score":"{:.2f}","latency_ms":"{:,}"}),
        width="stretch",
        height=280,
    )


def render_telemetry_table(df: pd.DataFrame):
    section("Filterable Telemetry")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("<span class='filter-lbl'>Phase</span>", unsafe_allow_html=True)
        sel_phase = st.selectbox("Phase", ["All"] + sorted(df["phase"].dropna().unique()),
                                 key="tp", label_visibility="collapsed")
    with f2:
        st.markdown("<span class='filter-lbl'>Environment</span>", unsafe_allow_html=True)
        sel_env   = st.selectbox("Environment", ["All"] + sorted(df["environment"].dropna().unique()),
                                 key="te", label_visibility="collapsed")
    with f3:
        st.markdown("<span class='filter-lbl'>Quick Filters</span>", unsafe_allow_html=True)
        fn_only   = st.checkbox("False Negatives only", key="tfn")
    with f4:
        st.markdown("<span class='filter-lbl'>&nbsp;</span>", unsafe_allow_html=True)
        unc_only  = st.checkbox("Uncertainty Flagged", key="tunc")

    filt = df.copy()
    if sel_phase != "All": filt = filt[filt["phase"] == sel_phase]
    if sel_env   != "All": filt = filt[filt["environment"] == sel_env]
    if fn_only:  filt = filt[filt["false_negative"]]
    if unc_only: filt = filt[filt["uncertainty_flag"]]

    st.markdown(
        f"<p style='color:#7a90b8;font-size:12px;margin:6px 0 10px;'>"
        f"Showing <b style='color:#6389ff'>{len(filt):,}</b> of {len(df):,} rows</p>",
        unsafe_allow_html=True,
    )
    display = filt[[
        "validation_id","phase","environment","ai_confidence_score",
        "actual_failure","failure_detected_by_ai","false_negative",
        "uncertainty_flag","latency_ms","timestamp",
    ]].reset_index(drop=True)

    st.dataframe(
        display.style.format({"ai_confidence_score":"{:.2f}","latency_ms":"{:,}"}),
        width="stretch",
        height=400,
    )


def render_sidebar(df: pd.DataFrame, m: dict):
    with st.sidebar:
        st.markdown(
            "<div style='padding:8px 0 16px;'>"
            "<div style='font-size:16px;font-weight:800;color:#c8d8ff;'>AI Validation</div>"
            "<div style='font-size:11px;color:#7a90b8;letter-spacing:1px;'>CONFIDENCE MONITOR</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

        st.markdown(
            f"<div style='color:#7a90b8;font-size:11px;margin-bottom:12px;'>"
            f"<b style='color:#6389ff;font-size:16px;'>{len(df):,}</b> rows &nbsp;·&nbsp; "
            f"<b style='color:#6389ff;'>{df['environment'].nunique()}</b> environments &nbsp;·&nbsp; "
            f"<b style='color:#6389ff;'>{df['phase'].nunique()}</b> phases"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;"
            "color:#7a90b8;margin-bottom:10px;font-weight:700;'>Quick Metrics</div>",
            unsafe_allow_html=True,
        )

        metric_defs = [
            ("AI Confidence",   f"{m['ai_confidence_index']:.1f}%",
             "#6389ff" if m["ai_confidence_index"] >= 85 else "#ff8800"),
            ("ECS",             f"{m['ecs']:.0f}%",
             "#00d97e" if m["ecs"] >= 80 else "#ff8800" if m["ecs"] >= 60 else "#ff4b4b"),
            ("False Neg. Rate", f"{m['false_negative_rate']:.1f}%",
             "#00d97e" if m["false_negative_rate"] <= 5 else "#ffd600" if m["false_negative_rate"] <= 10 else "#ff4b4b"),
            ("Precision",       f"{m['precision']:.1f}%",
             "#00d97e" if m["precision"] >= 80 else "#ff8800"),
            ("Confidence Gap",  f"{m['confidence_gap']:.1f}",
             "#00d97e" if m["confidence_gap"] <= 10 else "#ffd600" if m["confidence_gap"] <= 20 else "#ff4b4b"),
            ("RAI",             f"{m['rai']:.1f}",
             "#00d97e" if m["rai"] >= 70 else "#ffd600" if m["rai"] >= 50 else "#ff4b4b"),
            ("Uncertainty",     f"{m['uncertainty_rate']:.1f}%",
             "#00d97e" if m["uncertainty_rate"] <= 10 else "#ffd600"),
        ]
        for label, val, color in metric_defs:
            st.markdown(
                f"<div class='sb-metric'>"
                f"<span class='sb-label'>{label}</span>"
                f"<span class='sb-val' style='color:{color};'>{val}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr class='fancy-divider' style='margin-top:16px;'>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#5a6888;font-size:10px;text-align:center;margin-top:12px;'>"
            "AI Validation Confidence Monitor<br>Governance Platform v1.0</p>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    try:
        df = load_data()
    except (FileNotFoundError, RuntimeError) as e:
        st.error(str(e))
        st.stop()

    m = get_metrics(df)

    render_sidebar(df, m)
    render_header(m["risk"]["overall_severity"])
    render_executive_snapshot(m)
    render_kpis(m)
    render_gauges(m)
    render_phase_comparison(m["phase_before"], m["phase_after"])
    render_environment_analysis(m["env_metrics"], df)
    render_trends(df)
    render_risk_signals(m["risk"])
    render_uncertainty_table(df)
    render_telemetry_table(df)

    st.markdown(
        "<hr class='fancy-divider' style='margin:40px 0 16px;'>"
        "<p style='text-align:center;color:#5a6888;font-size:11px;padding-bottom:20px;'>"
        "AI Validation Confidence Monitor &nbsp;·&nbsp; Governance Platform v1.0</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class Theme:
    """Diseño Enterprise — No Country E-Commerce Churn Intelligence"""

    CANVAS_BG  = "#F0F4F8"
    TILE_BG    = "#FFFFFF"
    TEXT_COLOR = "#1A202C"
    ACCENT     = "#4F46E5"          # índigo principal
    ACCENT2    = "#10B981"          # verde éxito
    DANGER     = "#EF4444"
    WARNING    = "#F59E0B"
    INFO       = "#3B82F6"
    COLORS     = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
                  "#14B8A6", "#F43F5E", "#06B6D4", "#84CC16", "#F97316"]

    @staticmethod
    def apply_global_css():
        st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            .stApp {{
                background-color: {Theme.CANVAS_BG};
                color: {Theme.TEXT_COLOR};
            }}
            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%) !important;
                border-right: none !important;
            }}
            [data-testid="stSidebar"] * {{
                color: #E0E7FF !important;
            }}
            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stMultiSelect label {{
                color: #C7D2FE !important;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            [data-testid="stHeader"] {{ background-color: transparent !important; }}
            #MainMenu, footer, header {{ visibility: hidden; }}

            /* ── KPI Cards ────────────────────── */
            .kpi-card {{
                background: {Theme.TILE_BG};
                padding: 20px 18px;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
                text-align: center;
                transition: transform 0.2s;
            }}
            .kpi-card:hover {{ transform: translateY(-2px); }}
            .kpi-title {{
                font-size: 0.72rem;
                color: #64748B;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.8px;
                margin-bottom: 8px;
            }}
            .kpi-value {{
                font-size: 2rem;
                font-weight: 800;
                color: {Theme.TEXT_COLOR};
                line-height: 1.1;
            }}
            .kpi-sub {{
                font-size: 0.75rem;
                margin-top: 6px;
                font-weight: 500;
            }}
            .kpi-green  {{ color: {Theme.ACCENT2}; }}
            .kpi-red    {{ color: {Theme.DANGER};  }}
            .kpi-yellow {{ color: {Theme.WARNING}; }}
            .kpi-blue   {{ color: {Theme.INFO};    }}

            /* ── Section Headers ──────────────── */
            .section-header {{
                font-size: 0.72rem;
                font-weight: 700;
                color: #94A3B8;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin: 18px 0 10px 0;
                border-bottom: 1px solid #E2E8F0;
                padding-bottom: 6px;
            }}

            /* ── Badge / Tag ──────────────────── */
            .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 0.72rem;
                font-weight: 600;
            }}
            .badge-green  {{ background:#D1FAE5; color:#065F46; }}
            .badge-red    {{ background:#FEE2E2; color:#991B1B; }}
            .badge-yellow {{ background:#FEF3C7; color:#92400E; }}
            .badge-blue   {{ background:#DBEAFE; color:#1E40AF; }}
            .badge-purple {{ background:#EDE9FE; color:#5B21B6; }}

            /* ── Insight box ──────────────────── */
            .insight-box {{
                background: linear-gradient(135deg, #EEF2FF 0%, #F0FDF4 100%);
                border-left: 4px solid {Theme.ACCENT};
                border-radius: 0 10px 10px 0;
                padding: 14px 18px;
                margin: 10px 0;
                font-size: 0.88rem;
                color: #374151;
                line-height: 1.6;
            }}

            /* ── Streamlit containers ─────────── */
            div[data-testid="stVerticalBlock"] > div {{
                border-radius: 12px;
            }}
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def update_fig_layout(fig, height: int = 340):
        fig.update_layout(
            paper_bgcolor = Theme.TILE_BG,
            plot_bgcolor  = Theme.TILE_BG,
            font          = dict(family="Inter, Segoe UI, sans-serif", color=Theme.TEXT_COLOR, size=12),
            margin        = dict(l=12, r=12, t=40, b=12),
            colorway      = Theme.COLORS,
            height        = height,
            legend        = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                 font=dict(size=11)),
            title_font    = dict(size=13, color="#374151", family="Inter"),
        )
        fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=11))
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False, tickfont=dict(size=11))
        return fig


class UIComponents:

    @staticmethod
    def kpi(title: str, value: str, subtext: str = "", color: str = "green"):
        color_cls = f"kpi-{color}"
        st.markdown(
            f"""<div class="kpi-card">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub {color_cls}">{subtext}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    @staticmethod
    def section(label: str):
        st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

    @staticmethod
    def insight(text: str):
        st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

    @staticmethod
    def badge(text: str, color: str = "blue"):
        st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)


class ChartFactory:
    """Fábrica de gráficas con estilos Enterprise unificados."""

    @staticmethod
    def bar(df, x, y, color=None, title="", orientation="v", height=340):
        fig = px.bar(df, x=x, y=y, color=color, title=title,
                     orientation=orientation, text_auto=".2s")
        fig.update_traces(textfont_size=11, textposition="outside" if orientation=="v" else "inside")
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def pie(df, names, values, title="", hole=0.65, height=340):
        df_clean = df.copy()
        df_clean[values] = df_clean[values].abs()
        fig = px.pie(df_clean, names=names, values=values, hole=hole, title=title)
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          pull=[0.04] * len(df_clean))
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def scatter(df, x, y, size=None, color=None, title="", height=340):
        fig = px.scatter(df, x=x, y=y, size=size, color=color, title=title,
                         size_max=38, opacity=0.8)
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def treemap(df, path, values, color=None, title="", height=380):
        fig = px.treemap(df, path=path, values=values, color=color, title=title,
                         color_continuous_scale="RdYlGn_r")
        fig.update_traces(root_color="white", textinfo="label+value+percent entry")
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def line(df, x, y, color=None, title="", height=340):
        fig = px.line(df, x=x, y=y, color=color, title=title, markers=True)
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def area(df, x, y, color=None, title="", height=340):
        fig = px.area(df, x=x, y=y, color=color, title=title)
        fig.update_traces(opacity=0.75)
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def heatmap(df, x, y, z, title="", height=340):
        fig = px.density_heatmap(df, x=x, y=y, z=z, title=title,
                                 color_continuous_scale="Blues")
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def gauge(value, title, max_val=100, color="#EF4444", height=300):
        fig = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = value,
            title = {"text": title, "font": {"size": 13}},
            delta = {"reference": max_val * 0.3, "relative": False},
            gauge = {
                "axis": {"range": [None, max_val], "tickwidth": 1},
                "bar":  {"color": color, "thickness": 0.28},
                "steps": [
                    {"range": [0, max_val * 0.33], "color": "#DCFCE7"},
                    {"range": [max_val * 0.33, max_val * 0.66], "color": "#FEF9C3"},
                    {"range": [max_val * 0.66, max_val], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "#1A202C", "width": 3},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        ))
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def funnel(df, x, y, title="", height=340):
        fig = px.funnel(df, x=x, y=y, title=title)
        return Theme.update_fig_layout(fig, height)

    @staticmethod
    def horizontal_bar(df, x, y, color=None, title="", height=340):
        fig = px.bar(df, x=x, y=y, color=color, title=title,
                     orientation="h", text_auto=".2s")
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        return Theme.update_fig_layout(fig, height)

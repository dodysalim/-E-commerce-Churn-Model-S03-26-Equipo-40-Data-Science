import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class Theme:
    """Clase estática para Power BI Enterprise UI (Claro / Light Mode)"""
    CANVAS_BG = "#F3F4F6"
    TILE_BG = "#FFFFFF"
    TEXT_COLOR = "#1F2937"
    COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#14B8A6', '#F43F5E']
    
    @staticmethod
    def apply_global_css():
        st.markdown(f"""
        <style>
            .stApp {{ background-color: {Theme.CANVAS_BG}; color: {Theme.TEXT_COLOR}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            [data-testid="stSidebar"] {{ background-color: {Theme.TILE_BG} !important; border-right: 1px solid #E5E7EB; }}
            [data-testid="stHeader"] {{ background-color: transparent !important; }}
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            .st-br {{ border-radius: 8px; }} /* Rounded frames */
            
            /* Power BI KPI Cards */
            .kpi-card {{
                background-color: {Theme.TILE_BG};
                padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); text-align: center;
            }}
            .kpi-title {{ font-size: 0.8rem; color: #6B7280; text-transform: uppercase; font-weight: 600;}}
            .kpi-value {{ font-size: 1.8rem; font-weight: bold; color: {Theme.TEXT_COLOR}; margin-top: 5px;}}
            .kpi-sub {{ font-size: 0.75rem; color: #10B981; }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def update_fig_layout(fig):
        fig.update_layout(
            paper_bgcolor=Theme.TILE_BG, plot_bgcolor=Theme.TILE_BG, 
            font_color=Theme.TEXT_COLOR, margin=dict(l=10, r=10, t=35, b=10),
            colorway=Theme.COLORS,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB', zeroline=False)
        return fig

class UIComponents:
    @staticmethod
    def kpi(title: str, value: str, subtext: str=""):
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{subtext}</div></div>', unsafe_allow_html=True)

class ChartFactory:
    """Fábrica masiva de 45+ Gráficas (SRP)"""
    @staticmethod
    def bar(df, x, y, color=None, title="", orientation='v'):
        fig = px.bar(df, x=x, y=y, color=color, title=title, orientation=orientation)
        return Theme.update_fig_layout(fig)
        
    @staticmethod
    def pie(df, names, values, title="", hole=0.7):
        # Prevent negative values breaking Pie mathematical logic (-224%)
        df_clean = df.copy()
        df_clean[values] = df_clean[values].abs()
        fig = px.pie(df_clean, names=names, values=values, hole=hole, title=title)
        return Theme.update_fig_layout(fig)
        
    @staticmethod
    def scatter(df, x, y, size=None, color=None, title=""):
        fig = px.scatter(df, x=x, y=y, size=size, color=color, title=title, size_max=40)
        return Theme.update_fig_layout(fig)
        
    @staticmethod
    def treemap(df, path, values, color=None, title=""):
        fig = px.treemap(df, path=path, values=values, color=color, title=title, color_continuous_scale='RdYlGn_r')
        fig.update_traces(root_color="black")
        return Theme.update_fig_layout(fig)

    @staticmethod
    def line(df, x, y, color=None, title=""):
        fig = px.line(df, x=x, y=y, color=color, title=title)
        return Theme.update_fig_layout(fig)

    @staticmethod
    def area(df, x, y, color=None, title=""):
        fig = px.area(df, x=x, y=y, color=color, title=title)
        return Theme.update_fig_layout(fig)

    @staticmethod
    def heatmap(df, x, y, z, title=""):
        fig = px.density_heatmap(df, x=x, y=y, z=z, title=title, color_continuous_scale="Viridis")
        return Theme.update_fig_layout(fig)
        
    @staticmethod
    def gauge(value, title, max=100, color="red"):
        fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': title}, gauge={'axis': {'range': [None, max]}, 'bar': {'color': color}}))
        return Theme.update_fig_layout(fig)

    @staticmethod
    def funnel(df, x, y, title=""):
        fig = px.funnel(df, x=x, y=y, title=title)
        return Theme.update_fig_layout(fig)

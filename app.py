import streamlit as st
import requests
import pandas as pd

# 頁面配置
st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# 亮色/暗色主題 CSS
def get_theme_css(is_light):
    if is_light:
        return """
        <style>
            .stApp { background-color: #f0f2f6; color: #1e1e1e; }
            .metric-card { background: #ffffff; border: 1px solid #d1d5db; }
            h1, h2 { color: #2563eb; }
        </style>
        """
    else:
        return """
        <style>
            .stApp { background-color: #050505; color: #00ff41; }
            .metric-card { background: #111; border: 1px solid #00ff41; }
            h1, h2 { color: #00d2ff; }
        </style>
        """

# 主題切換狀態
if "light_mode" not in st.session_state: st.session_state.light_mode = False
is_light = st.sidebar.toggle("☀️ LIGHT MODE", key="light_mode")
st.markdown(get_theme_css(is_light), unsafe_allow_html=True)

# 隱藏浮水印與選單 (強制隱藏)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 儀表板內容 ---
st.title("🛰️ GNSS & SDR MISSION CONTROL")

# 你的其他功能程式碼...

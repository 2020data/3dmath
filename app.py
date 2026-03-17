import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# 設定網頁標題
st.set_page_config(page_title="3D 數學函數繪圖器", layout="wide")
st.title("📐 3D 數學函數繪圖器 (進階質感版)")

# 側邊欄：參數設定
with st.sidebar:
    st.header("⚙️ 參數設定")
    func_str = st.text_input("輸入函數 f(x, y):", value="sin(sqrt(x**2 + y**2))")
    
    st.subheader("🎨 外觀設定")
    # 1. 顏色主題選單
    colorscale = st.selectbox(
        "色彩主題 (Colormap)", 
        ['Viridis', 'Plasma', 'Inferno', 'Magma', 'Ocean', 'IceFire', 'Turbo', 'Jet']
    )
    
    # 2. 材質質感選單
    material = st.selectbox(
        "立體質感 (Material)", 
        ['預設霧面 (Matte)', '高反光塑膠 (Plastic)', '金屬光澤 (Metallic)', '自發光 (Glowing)']
    )
    
    # 定義不同質感的 Plotly 光影參數 (ambient, diffuse, specular, roughness, fresnel)
    lighting_effects = {
        '預設霧面 (Matte)': dict(ambient=0.6, diffuse=0.8, specular=0.1, roughness=0.5, fresnel=0.2),
        '高反光塑膠 (Plastic)': dict(ambient=0.5, diffuse=0.7, specular=0.9, roughness=0.1, fresnel=0.5),
        '金屬光澤 (Metallic)': dict(ambient=0.4, diffuse=0.5, specular=0.8, roughness=0.2, fresnel=0.8),
        '自發光 (Glowing)': dict(ambient=0.9, diffuse=0.2, specular=0.1, roughness=0.9, fresnel=0.1)
    }

    st.subheader("📐 座標軸範圍")
    x_min, x_max = st.slider("X 軸範圍", -20.0, 20.0, (-10.0, 10.0))
    y_min, y_max = st.slider("Y 軸範圍", -20.0, 20.0, (-10.0, 10.0))
    
    st.subheader("網格解析度")
    resolution = st.slider("解析度 (越大越平滑)", 10, 150, 60)

# 主要繪圖區
try:
    # 安全地解析數學函數
    x, y = sp.symbols('x y')
    transformations = standard_transformations + (implicit_multiplication_application,)
    expr = parse_expr(func_str, transformations=transformations)
    f = sp.lambdify((x, y), expr, "numpy")

    # 產生網格資料
    x_vals = np.linspace(x_min, x_max, resolution)
    y_vals = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = f(X, Y)

    if np.isscalar(Z):
        Z = np.full_like(X, Z)
    elif Z.shape != X.shape:
        Z = np.broadcast_to(Z, X.shape)

    # 建立 Plotly 3D 圖表，並套用顏色與光影設定
    fig = go.Figure(data=[go.Surface(
        z=Z, x=X, y=Y, 
        colorscale=colorscale,                     # 套用顏色主題
        lighting=lighting_effects[material]        # 套用光影與材質質感
    )])
    
    fig.update_layout(
        title=f"<b>f(x, y) = {func_str}</b>",
        autosize=True,
        height=700,
        margin=dict(l=0, r=0, b=0, t=50),
        scene=dict(
            xaxis_title='X 軸',
            yaxis_title='Y 軸',
            zaxis_title='Z 軸'
        )
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("⚠️ 函數解析錯誤或計算失敗！請檢查數學函數的語法。")

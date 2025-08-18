# --- Path bootstrap BEFORE third-party imports ---
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root that contains 'src/'
if (ROOT / "src").exists() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data.loaders import load_sales_data

st.set_page_config(page_title="Control de Precios", layout="wide")
st.title("Dashboard de Control de Precios")

csv_path = ROOT / "data" / "processed" / "sales.csv"
if not csv_path.exists():
    st.warning("No se encontró 'data/processed/sales.csv'. Usando datos sintéticos de ejemplo.")
    df = load_sales_data()
else:
    df = load_sales_data(csv_path)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

st.sidebar.header("Filtros")
lines = ["(Todas)"] + sorted([x for x in df["product_line"].dropna().unique()])
line_sel = st.sidebar.selectbox("Línea de producto", lines, index=0)
if line_sel != "(Todas)":
    df = df[df["product_line"] == line_sel]
skus = ["(Todos)"] + sorted([x for x in df.get("sku", pd.Series()).dropna().unique()])
sku_sel = st.sidebar.selectbox("SKU", skus, index=0)
if sku_sel != "(Todos)" and "sku" in df.columns:
    df = df[df["sku"] == sku_sel]

c1, c2, c3 = st.columns(3)
c1.metric("Líneas en vista", f"{df['product_line'].nunique()}")
c2.metric("Ventas totales (unid.)", f"{int(df['sales'].sum()):,}")
c3.metric("Precio promedio", f"{df['price'].mean():.2f}")

g = df.groupby(["date","product_line"])["sales"].sum().reset_index()
fig = px.line(g, x="date", y="sales", color="product_line", title="Ventas diarias por Línea de Producto")
st.plotly_chart(fig, use_container_width=True)

rpt_path = ROOT / "docs" / "reporte_impacto_financiero.csv"
if rpt_path.exists():
    st.subheader("Simulador de escenarios (margen total)")
    rpt = pd.read_csv(rpt_path)
    st.bar_chart(rpt.set_index("price")["total_margin"])

st.subheader("Descargas")
st.download_button("Dataset procesado (CSV)", data=df.to_csv(index=False).encode("utf-8"),
                   file_name="sales_filtered.csv", mime="text/csv")

import pandas as pd
from pathlib import Path
import numpy as np

SKU_LINES = {"A":"Bebidas","B":"Snacks","C":"Limpieza","D":"Lácteos"}
def assign_product_line(sku: str) -> str:
    return SKU_LINES.get(str(sku), "Otros")

def load_csv_if_exists(path: str):
    p = Path(path); return pd.read_csv(p) if p.exists() else None

def load_sales_data(path: str = None) -> pd.DataFrame:
    if path:
        df = load_csv_if_exists(path)
        if df is not None: return df
    df = load_csv_if_exists("data/processed/sales.csv")
    if df is not None: return df
    rng = pd.date_range("2023-01-01", periods=400, freq="D")
    df = pd.DataFrame({
        "date": rng,
        "store_id": np.random.randint(1, 51, size=len(rng)),
        "sku": np.random.choice(["A","B","C","D"], size=len(rng)),
        "product_line": None,
        "price": np.random.uniform(3, 20, size=len(rng)).round(2),
        "inventory": np.random.randint(50, 500, size=len(rng)),
        "competitor_price": np.random.uniform(3, 20, size=len(rng)).round(2),
        "promo": np.random.binomial(1, 0.2, size=len(rng)),
    })
    base = 120 - (df["price"] ** 1.1) * 2.3 + df["promo"] * 15
    noise = np.random.normal(0, 6, size=len(rng))
    df["sales"] = (base + noise).clip(0).round().astype(int)
    df["product_line"] = df["sku"].map(assign_product_line)
    return df

def load_external_data(path: str = None) -> pd.DataFrame:
    df = load_csv_if_exists(path or "data/external/external_factors.csv")
    if df is not None: return df
    rng = pd.date_range("2023-01-01", periods=400, freq="D")
    return pd.DataFrame({
        "date": rng,
        "holiday": (rng.dayofweek >= 5).astype(int),
        "rain_mm": np.random.gamma(2.0, 1.5, size=len(rng)).round(2),
        "cpi": 100 + np.linspace(0, 5, len(rng)),
    })

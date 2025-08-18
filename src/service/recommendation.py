import pandas as pd, numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from src.data.loaders import load_sales_data
from src.models.elasticity import price_elasticity_loglog

def _load_forecast(project_root: Path):
    fp = project_root / "models" / "trained_models" / "prophet_fcst.csv"
    if not fp.exists(): return None
    df = pd.read_csv(fp)
    if "forecast" not in df.columns and "yhat" in df.columns:
        df = df.rename(columns={"ds":"date","yhat":"forecast"})
    return df

def _price_grid_from_artifacts(project_root: Path, df_subset: pd.DataFrame):
    gp = project_root / "models" / "model_configs" / "qlearning_grid.txt"
    if gp.exists():
        try:
            vals = [float(x.strip()) for x in gp.read_text().splitlines() if x.strip()]
            if len(vals) >= 5: 
                import numpy as np
                return np.array(sorted(vals))
        except Exception:
            pass
    lo, hi = float(df_subset["price"].quantile(0.05)), float(df_subset["price"].quantile(0.95))
    if not np.isfinite(lo) or not np.isfinite(hi) or lo >= hi:
        lo, hi = float(df_subset["price"].min()), float(df_subset["price"].max())
    import numpy as np
    return np.linspace(lo, hi, 15)

def _base_demand(project_root: Path, df_subset: pd.DataFrame) -> float:
    fcst = _load_forecast(project_root)
    if fcst is not None and "forecast" in fcst.columns:
        future = fcst.copy()
        if "date" in future.columns and "date" in df_subset.columns:
            try:
                future["date"] = pd.to_datetime(future["date"], errors="coerce")
                min_hist = df_subset["date"].max()
                future = future[future["date"] > min_hist]
            except Exception: pass
        if len(future): return float(future["forecast"].mean())
    recent = df_subset.sort_values("date").tail(28)
    return float(recent["sales"].mean()) if len(recent) else float(df_subset["sales"].mean())

def _estimate_elasticity(df_subset: pd.DataFrame) -> float:
    import numpy as np
    try:
        res = price_elasticity_loglog(df_subset, y="sales", x="price", controls=["promo","competitor_price"])
        elas = float(res["elasticity"])
        if np.isfinite(elas): return elas
    except Exception: pass
    c = float(df_subset[["price","sales"]].corr().iloc[0,1])
    elas = -1.2 + (-1.0)*c
    return float(elas)

def _demand_at_price(base_demand: float, p: float, p_ref: float, elasticity: float) -> float:
    if p_ref <= 0: p_ref = max(0.01, p)
    return max(0.0, base_demand * (p / p_ref) ** elasticity)

def recommend_price(project_root: Path, sku: Optional[str]=None, product_line: Optional[str]=None,
                    cost: float = 5.0) -> Dict[str, Any]:
    df = load_sales_data(project_root / "data" / "processed" / "sales.csv")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    sub = df.copy()
    if product_line is not None:
        sub = sub[sub["product_line"] == product_line]
    if sku is not None and "sku" in sub.columns:
        sub = sub[sub["sku"] == sku]
    if sub.empty:
        raise ValueError("No hay datos para el filtro solicitado (sku/product_line).")
    price_grid = _price_grid_from_artifacts(project_root, sub)
    p_ref = float(sub["price"].mean())
    D0 = _base_demand(project_root, sub)
    E = _estimate_elasticity(sub)
    margins = []
    for p in price_grid:
        demand = _demand_at_price(D0, p, p_ref, E)
        margins.append((p, (p - cost) * demand))
    best_price, best_margin = max(margins, key=lambda x: x[1])
    return {
        "sku": sku, "product_line": product_line,
        "recommended_price": float(best_price),
        "best_margin": float(best_margin),
        "price_grid": list(map(float, price_grid)),
        "elasticity": float(E),
        "base_demand": float(D0),
        "reference_price": float(p_ref),
        "cost": float(cost),
    }

import statsmodels.api as sm
import pandas as pd
import numpy as np
def price_elasticity_loglog(df: pd.DataFrame, y="sales", x="price", controls=None):
    controls = controls or []
    d = df[[y, x] + controls].copy().replace(0, np.nan).dropna()
    d["ln_y"] = np.log(d[y]); d["ln_x"] = np.log(d[x])
    X = sm.add_constant(d[["ln_x"] + controls])
    model = sm.OLS(d["ln_y"], X).fit()
    elasticity = model.params.get("ln_x", float("nan"))
    return {"elasticity": float(elasticity), "summary": model.summary().as_text()}

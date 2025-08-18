from prophet import Prophet
import pandas as pd
def forecast_demand_prophet(df: pd.DataFrame, date_col="date", y_col="sales", periods=30) -> pd.DataFrame:
    m = Prophet()
    tmp = df[[date_col, y_col]].rename(columns={date_col:"ds", y_col:"y"})
    m.fit(tmp)
    future = m.make_future_dataframe(periods=periods)
    fcst = m.predict(future)
    return fcst[["ds","yhat","yhat_lower","yhat_upper"]]

def forecast_demand_lstm(series, lookback=14, epochs=5):
    import numpy as np
    from tensorflow.keras import layers, models
    values = series.values.astype("float32")
    X, y = [], []
    for i in range(len(values)-lookback):
        X.append(values[i:i+lookback]); y.append(values[i+lookback])
    import numpy as np
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    model = models.Sequential([layers.Input(shape=(lookback,1)), layers.LSTM(32), layers.Dense(1)])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)
    preds = []
    last = values[-lookback:].copy()
    for _ in range(30):
        x = last.reshape((1, lookback, 1))
        p = float(model.predict(x, verbose=0)[0,0])
        preds.append(p)
        last = np.append(last[1:], p)
    return pd.Series(preds)

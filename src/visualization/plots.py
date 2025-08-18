import matplotlib.pyplot as plt
def plot_series(df, date_col="date", y_col="sales", title="Serie de ventas"):
    ax = df.plot(x=date_col, y=y_col)
    ax.set_title(title); ax.set_xlabel("Fecha"); ax.set_ylabel(y_col)
    return ax

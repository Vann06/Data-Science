import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calcular_metricas(y_real, y_pred):
    mae = mean_absolute_error(y_real, y_pred)
    rmse = np.sqrt(mean_squared_error(y_real, y_pred))

    return {
        "MAE": mae,
        "RMSE": rmse,
    }
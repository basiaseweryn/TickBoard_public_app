import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def calculate_metrics(y_true, y_pred):
    if hasattr(y_true, 'values'):
        y_true = y_true.values.flatten()
    if hasattr(y_pred, 'values'):
        y_pred = y_pred.values.flatten()
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'mean_true': np.mean(y_true),
        'mean_pred': np.mean(y_pred),
        'std_true': np.std(y_true),
        'std_pred': np.std(y_pred)
    }
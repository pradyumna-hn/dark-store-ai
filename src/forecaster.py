"""Core forecasting logic using Prophet and LightGBM."""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, Optional

from src.features import build_forecast_features


def _rolling_average_forecast(
    orders_df: pd.DataFrame,
    sku_id: str,
    store_id: str,
    horizon: int = 7,
) -> pd.DataFrame:
    """Simple 7-day rolling average fallback forecast.

    Used when there is insufficient data for Prophet or LightGBM.

    Args:
        orders_df: Orders DataFrame.
        sku_id: SKU identifier.
        store_id: Store identifier.
        horizon: Number of days to forecast.

    Returns:
        DataFrame with columns [ds, yhat, yhat_lower, yhat_upper, model].
    """
    warnings.warn(
        f"SKU {sku_id} / {store_id}: using 7-day rolling average fallback.",
        stacklevel=2,
    )
    features = build_forecast_features(orders_df, sku_id, store_id)
    if features is None or features.empty:
        avg = 0.0
    else:
        avg = features["daily_demand"].tail(7).mean()

    last_date = features["ds"].max() if features is not None else pd.Timestamp.today()
    dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    return pd.DataFrame({
        "ds": dates,
        "yhat": avg,
        "yhat_lower": max(0, avg * 0.7),
        "yhat_upper": avg * 1.3,
        "model": "rolling_avg",
    })


def _prophet_forecast(
    daily_df: pd.DataFrame,
    horizon: int = 7,
) -> pd.DataFrame:
    """Fit a Prophet model and return forecast.

    Args:
        daily_df: Daily demand DataFrame from build_forecast_features().
        horizon: Days to forecast.

    Returns:
        DataFrame with columns [ds, yhat, yhat_lower, yhat_upper, model].
    """
    try:
        from prophet import Prophet  # noqa: PLC0415
    except ImportError:
        raise ImportError("prophet is not installed. Run: pip install prophet")

    prophet_df = daily_df[["ds", "daily_demand"]].rename(
        columns={"daily_demand": "y"}
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = Prophet(
            weekly_seasonality=True,
            yearly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            interval_width=0.80,
        )
        model.fit(prophet_df)

    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).copy()
    result["yhat"] = result["yhat"].clip(lower=0)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0)
    result["model"] = "prophet"
    return result.reset_index(drop=True)


def _lgbm_forecast(
    daily_df: pd.DataFrame,
    horizon: int = 7,
) -> pd.DataFrame:
    """Train a LightGBM regressor and predict next N days.

    Args:
        daily_df: Daily demand DataFrame from build_forecast_features().
        horizon: Days to forecast.

    Returns:
        DataFrame with columns [ds, yhat, yhat_lower, yhat_upper, model].
    """
    try:
        import lightgbm as lgb  # noqa: PLC0415
    except ImportError:
        raise ImportError("lightgbm is not installed. Run: pip install lightgbm")

    feature_cols = [
        "rolling_7d_avg", "rolling_14d_avg",
        "day_of_week", "is_weekend",
        "is_month_start", "is_month_end",
        "lag_1", "lag_7", "week_of_year",
    ]

    df = daily_df.dropna(subset=feature_cols + ["daily_demand"])
    X = df[feature_cols].values
    y = df["daily_demand"].values

    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=15,
        random_state=42,
        verbose=-1,
    )
    model.fit(X, y)

    # Build future rows
    last_row = daily_df.iloc[-1].copy()
    last_date = pd.Timestamp(daily_df["ds"].max())
    future_rows = []
    for i in range(1, horizon + 1):
        future_date = last_date + pd.Timedelta(days=i)
        row = {
            "ds": future_date,
            "daily_demand": last_row["daily_demand"],
            "rolling_7d_avg": last_row["rolling_7d_avg"],
            "rolling_14d_avg": last_row["rolling_14d_avg"],
            "day_of_week": future_date.dayofweek,
            "is_weekend": int(future_date.dayofweek >= 5),
            "is_month_start": int(future_date.is_month_start),
            "is_month_end": int(future_date.is_month_end),
            "lag_1": last_row["daily_demand"],
            "lag_7": last_row["lag_7"],
            "week_of_year": future_date.isocalendar()[1],
        }
        future_rows.append(row)

    future_df = pd.DataFrame(future_rows)
    X_future = future_df[feature_cols].values
    preds = model.predict(X_future).clip(min=0)

    std = daily_df["daily_demand"].std()
    return pd.DataFrame({
        "ds": future_df["ds"],
        "yhat": preds,
        "yhat_lower": (preds - 1.28 * std).clip(min=0),
        "yhat_upper": preds + 1.28 * std,
        "model": "lgbm",
    })


def forecast_sku(
    orders_df: pd.DataFrame,
    sku_id: str,
    store_id: str,
    horizon: int = 7,
    method: str = "prophet",
) -> pd.DataFrame:
    """Forecast demand for a single SKU and store.

    Tries the requested method first, falls back to rolling average if needed.

    Args:
        orders_df: Orders DataFrame from data_loader.load_orders().
        sku_id: SKU identifier.
        store_id: Store identifier.
        horizon: Number of days to forecast.
        method: Forecasting method — "prophet" (default) or "lgbm".

    Returns:
        DataFrame with columns [ds, yhat, yhat_lower, yhat_upper, model].
    """
    daily_df = build_forecast_features(orders_df, sku_id, store_id)

    if daily_df is None or len(daily_df) < 30:
        return _rolling_average_forecast(orders_df, sku_id, store_id, horizon)

    try:
        if method == "prophet":
            return _prophet_forecast(daily_df, horizon)
        elif method == "lgbm":
            return _lgbm_forecast(daily_df, horizon)
        else:
            raise ValueError(f"Unknown forecasting method: {method}")
    except Exception as exc:  # noqa: BLE001
        warnings.warn(
            f"SKU {sku_id} / {store_id}: {method} failed ({exc}). "
            "Falling back to rolling average.",
            stacklevel=2,
        )
        return _rolling_average_forecast(orders_df, sku_id, store_id, horizon)


def forecast_all_top_skus(
    orders_df: pd.DataFrame,
    top_skus: pd.DataFrame,
    store_id: str,
    horizon: int = 7,
    method: str = "prophet",
) -> Dict[str, pd.DataFrame]:
    """Run forecasts for all top SKUs in a store.

    Args:
        orders_df: Orders DataFrame.
        top_skus: DataFrame returned by data_loader.get_top_skus().
        store_id: Store to forecast for.
        horizon: Days to forecast.
        method: Forecasting method — "prophet" or "lgbm".

    Returns:
        Dictionary mapping sku_id -> forecast DataFrame.
    """
    forecasts: Dict[str, pd.DataFrame] = {}
    total = len(top_skus)

    for i, row in top_skus.iterrows():
        sku_id = row["sku_id"]
        sku_name = row["sku_name"]
        print(f"  [{i + 1}/{total}] Forecasting {sku_name} ({sku_id}) ...", end=" ")
        try:
            fc = forecast_sku(orders_df, sku_id, store_id, horizon, method)
            forecasts[sku_id] = fc
            print(f"✓ ({fc['model'].iloc[0]})")
        except Exception as exc:  # noqa: BLE001
            warnings.warn(f"Skipping {sku_id}: {exc}")
            print(f"✗ (skipped)")

    return forecasts


def evaluate_forecast(
    actuals: pd.Series,
    predictions: pd.Series,
) -> Dict[str, float]:
    """Evaluate forecast quality.

    Args:
        actuals: Actual demand values.
        predictions: Predicted demand values.

    Returns:
        Dictionary with MAE and MAPE metrics.
    """
    actuals = np.array(actuals, dtype=float)
    predictions = np.array(predictions, dtype=float)

    mae = float(np.mean(np.abs(actuals - predictions)))

    non_zero = actuals != 0
    if non_zero.any():
        mape = float(np.mean(np.abs((actuals[non_zero] - predictions[non_zero]) / actuals[non_zero])) * 100)
    else:
        mape = float("nan")

    print(f"  MAE  : {mae:.2f}")
    print(f"  MAPE : {mape:.1f}%")
    return {"mae": mae, "mape": mape}

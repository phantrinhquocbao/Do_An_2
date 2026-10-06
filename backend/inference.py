"""Shared Yahoo data preparation and inference; no web server is required."""

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "lstm_vn30_model.h5"
SCALER_PATH = BASE_DIR / "scaler.pkl"
TIME_STEPS = 60
OHLCV = ["Open", "High", "Low", "Close", "Volume"]
# Exact order used by the original training notebook (scaler fitted on .values).
FEATURES = ["Open_VN", "High_VN", "Low_VN", "Close_VN", "Volume_VN", "Close_US"]
TARGET_INDEX = FEATURES.index("Close_VN")


def load_data(ticker, start_date, end_date):
    """Daily OHLCV with a sorted, timezone-free Date index; end is exclusive.

    Bare Vietnamese symbols use the requested .VN Yahoo suffix. Missing Yahoo
    coverage is an error, never substituted with another market or fake prices.
    """
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Mã chứng khoán không được để trống.")
    if not symbol.startswith("^") and "." not in symbol:
        symbol += ".VN"
    frame = yf.download(
        symbol, start=start_date, end=end_date, interval="1d",
        # Keep VN price levels; preserve the old adjusted S&P 500 Close series.
        auto_adjust=symbol.startswith("^"), actions=False, timeout=20,
        progress=False, threads=False, group_by="column", multi_level_index=False,
    )
    if frame is None or frame.empty:
        raise ValueError(f"Yahoo Finance không trả dữ liệu cho {symbol} trong khoảng ngày đã chọn.")
    if not symbol.startswith("^"):
        currency = yf.Ticker(symbol).get_history_metadata().get("currency")
        if currency != "VND":
            raise ValueError(
                f"Không xác nhận được giá VND cho {symbol} (currency={currency}); "
                "không đưa giá khác đơn vị vào scaler VN30."
            )
    return normalize_ohlcv(frame, symbol)


def normalize_ohlcv(frame, symbol):
    """Keep only the five model price inputs, even with Yahoo MultiIndex columns."""
    if isinstance(frame.columns, pd.MultiIndex):
        ticker_levels = [i for i in range(frame.columns.nlevels)
                         if symbol in frame.columns.get_level_values(i)]
        if len(ticker_levels) != 1:
            raise ValueError(f"Cấu trúc cột Yahoo không hợp lệ cho {symbol}.")
        frame = frame.xs(symbol, axis=1, level=ticker_levels[0])
    if isinstance(frame.columns, pd.MultiIndex):
        raise ValueError(f"Cấu trúc cột Yahoo còn nhiều cấp cho {symbol}.")
    frame = frame.rename(columns={c: str(c).strip().title() for c in frame.columns})
    if frame.columns.duplicated().any():
        raise ValueError(f"Dữ liệu {symbol} có cột trùng tên.")
    missing = [column for column in OHLCV if column not in frame.columns]
    if missing:
        raise ValueError(f"Dữ liệu {symbol} thiếu cột: {', '.join(missing)}")
    # Explicit selection discards Adj Close, Dividends, Stock Splits and extras.
    frame = frame.loc[:, OHLCV].copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce").tz_localize(None).normalize()
    frame.index.name = "Date"
    frame = frame.loc[frame.index.notna()]
    frame = frame.loc[~frame.index.duplicated(keep="last")].sort_index()
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    if frame.empty:
        raise ValueError(f"Dữ liệu {symbol} không có dòng OHLCV hợp lệ.")
    if (frame[OHLCV[:4]] <= 0).any().any() or (frame["Volume"] < 0).any():
        raise ValueError(f"Dữ liệu {symbol} có giá hoặc khối lượng không hợp lệ.")
    return frame


def load_features(ticker, start_date, end_date):
    vn = load_data(ticker, start_date, end_date).rename(columns=dict(zip(OHLCV, FEATURES[:5])))
    us = load_data("^GSPC", start_date, end_date)[["Close"]].rename(columns={"Close": "Close_US"})
    # Preserve the original inner join by trading date and feature order.
    features = prepare_features(vn.join(us, how="inner"))
    if len(features) < TIME_STEPS:
        raise ValueError(f"Chỉ có {len(features)} phiên chung VN/S&P 500; cần ít nhất {TIME_STEPS}.")
    return features


def prepare_features(frame):
    """Select exact training names/order and reject incomplete/non-finite rows."""
    if frame.columns.duplicated().any():
        raise ValueError("Input model có cột trùng tên.")
    missing = [name for name in FEATURES if name not in frame.columns]
    if missing:
        raise ValueError(f"Input model thiếu cột: {', '.join(missing)}")
    frame = frame.loc[:, FEATURES].apply(pd.to_numeric, errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    if frame.empty:
        raise ValueError("Không còn dữ liệu hợp lệ sau chuẩn hóa 6 đặc trưng.")
    return frame


def load_artifacts():
    # Lazy imports keep data pages usable and surface load errors in Streamlit.
    import joblib
    from keras.models import load_model

    for path in (MODEL_PATH, SCALER_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file: {path.name}")
    model = load_model(MODEL_PATH, compile=False)
    scaler = joblib.load(SCALER_PATH)
    if tuple(model.input_shape[1:]) != (TIME_STEPS, len(FEATURES)):
        raise ValueError(f"Model yêu cầu input {model.input_shape}, không khớp (None, 60, 6).")
    if getattr(scaler, "n_features_in_", None) != len(FEATURES):
        raise ValueError("Scaler không khớp 6 đặc trưng của model.")
    names = getattr(scaler, "feature_names_in_", None)
    if names is not None and list(names) != FEATURES:
        raise ValueError(f"Tên/thứ tự cột scaler không khớp: {list(names)}")
    return model, scaler


def scale_features(features, scaler):
    features = prepare_features(features)
    if getattr(scaler, "n_features_in_", None) != len(FEATURES):
        raise ValueError("Scaler không khớp 6 đặc trưng của model.")
    names = getattr(scaler, "feature_names_in_", None)
    if names is not None and list(names) != FEATURES:
        raise ValueError(f"Tên/thứ tự cột scaler không khớp: {list(names)}")
    # The saved scaler was fitted on an ndarray; preserve that input contract.
    data = features if hasattr(scaler, "feature_names_in_") else features.to_numpy()
    scaled = scaler.transform(data)
    if not np.isfinite(scaled).all():
        raise ValueError("Dữ liệu sau chuẩn hóa chứa NaN hoặc vô cực.")
    return scaled


def predict_price(features, model, scaler):
    scaled = scale_features(features, scaler)
    if len(scaled) < TIME_STEPS:
        raise ValueError("Không đủ 60 phiên hợp lệ sau dropna để dự báo.")
    x_input = np.asarray([scaled[-TIME_STEPS:]], dtype=np.float32)
    if x_input.shape != (1, TIME_STEPS, len(FEATURES)) or not np.isfinite(x_input).all():
        raise ValueError("Tensor đầu vào phải hữu hạn và có kích thước (1, 60, 6).")
    output = np.asarray(model(x_input, training=False))
    if output.shape != (1, 1) or not np.isfinite(output).all():
        raise ValueError("Model trả kết quả không hợp lệ.")
    inverse_input = np.zeros((1, len(FEATURES)))
    inverse_input[0, TARGET_INDEX] = float(output[0, 0])
    price = float(scaler.inverse_transform(inverse_input)[0, TARGET_INDEX])
    if not np.isfinite(price) or price <= 0:
        raise ValueError("Giá dự báo không hợp lệ.")
    return price

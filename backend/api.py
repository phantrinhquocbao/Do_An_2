from fastapi import FastAPI
import yfinance as yf
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import uvicorn
import os

app = FastAPI()

# Khởi tạo mô hình và bộ chuẩn hóa
# 1. Lấy vị trí chính xác của thư mục 'backend' (nơi đang chứa file api.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Ghép đường dẫn đó với tên file AI của ông
MODEL_PATH = os.path.join(BASE_DIR, "lstm_vn30_model.h5")

# 3. Load mô hình bằng cái đường dẫn xịn vừa tạo
model = load_model(MODEL_PATH)
# Gọi thước đo ra để xài
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
scaler = joblib.load(SCALER_PATH)

@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        # Tải dữ liệu 6 tháng gần nhất
        stock_vn = yf.Ticker(f"{ticker}.VN")
        stock_us = yf.Ticker("^GSPC")
        
        df_vn = stock_vn.history(period="6mo")
        df_us = stock_us.history(period="6mo")

        if df_vn.empty:
            return {"error": "Không tìm thấy dữ liệu cho mã cổ phiếu này."}

        df_vn.index = df_vn.index.tz_localize(None)
        df_us.index = df_us.index.tz_localize(None)

        df = pd.DataFrame({
            'Close_VN': df_vn['Close'],
            'Volume_VN': df_vn['Volume'],
            'Close_US': df_us['Close']
        })

        # Tính toán chỉ báo kỹ thuật
        delta = df['Close_VN'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        rs = gain.ewm(com=13, min_periods=14).mean() / loss.ewm(com=13, min_periods=14).mean()
        df['RSI_14'] = 100 - (100 / (1 + rs))

        df['MACD'] = df['Close_VN'].ewm(span=12, adjust=False).mean() - df['Close_VN'].ewm(span=26, adjust=False).mean()
        df.dropna(inplace=True)

        feature_cols = ['Close_VN', 'Volume_VN', 'Close_US', 'RSI_14', 'MACD']
        dataset = df[feature_cols].values

        # Xử lý dự báo
        scaled_data = scaler.transform(dataset) 
        last_60_days = scaled_data[-60:]
        
        if len(last_60_days) < 60:
             return {"error": "Chưa đủ dữ liệu 60 ngày để thực hiện dự báo."}
             
        X_input = np.array([last_60_days])
        predicted_scaled = model.predict(X_input)

        # Chuyển đổi giá trị dự báo về đơn vị VNĐ
        dummy_array = np.zeros((1, 5))
        dummy_array[0, 0] = predicted_scaled[0][0]
        predicted_price = scaler.inverse_transform(dummy_array)[0, 0]

        return {
            "ticker": ticker,
            "predicted_price_vnd": float(predicted_price)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
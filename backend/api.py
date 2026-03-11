from fastapi import FastAPI
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import uvicorn
import os
import yfinance as yf
from vnstock import stock_historical_data
from datetime import datetime, timedelta

app = FastAPI()

# Thêm dòng này vào api.py để có thể gọi từ web
@app.get("/update")
def trigger_update():
    try:
        from cap_nhat_model import cap_nhat_chinh
        cap_nhat_chinh()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

# 1. Khởi tạo đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "lstm_vn30_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# 2. Tải não bộ và phễu lọc
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Cấu hình 6 cột chuẩn xác với mô hình đã train
FEATURES = ['Open_VN', 'High_VN', 'Low_VN', 'Close_VN', 'Volume_VN', 'Close_US']
TARGET_INDEX = 3 # Vị trí cột Close_VN

# ... (Phần đầu giữ nguyên) ...

@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        # Tăng lên 150 ngày để đảm bảo sau khi gộp vẫn đủ 60 ngày giao dịch
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d')

        print(f"🔄 Đang lấy dữ liệu từ {start_date} đến {end_date}...")

        # 1. Tải chứng khoán VN
        df_vn = stock_historical_data(symbol=ticker.upper(), start_date=start_date, end_date=end_date, resolution='1D', type='stock')
        
        # ... (Phần còn lại y hệt như cũ) ...
        if df_vn.empty:
            return {"error": f"Không tìm thấy dữ liệu vnstock cho mã {ticker}."}

        df_vn = df_vn[['time', 'open', 'high', 'low', 'close', 'volume']]
        df_vn.columns = ['Date', 'Open_VN', 'High_VN', 'Low_VN', 'Close_VN', 'Volume_VN']
        df_vn['Date'] = pd.to_datetime(df_vn['Date'])

        # 2. Tải S&P 500 bằng yfinance
        df_us = yf.download('^GSPC', start=start_date, end=end_date, progress=False)
        if isinstance(df_us.columns, pd.MultiIndex):
            df_us = df_us['Close'].reset_index()
        else:
            df_us = df_us[['Close']].reset_index()
        df_us.columns = ['Date', 'Close_US']
        df_us['Date'] = pd.to_datetime(df_us['Date']).dt.tz_localize(None)

        # 3. Gộp bảng và điền khuyết
        df = pd.merge(df_vn, df_us, on='Date', how='inner').ffill()

        if len(df) < 60:
            return {"error": "Chưa đủ dữ liệu 60 ngày giao dịch để dự báo."}

        # 4. Lọc đúng 6 cột
        dataset = df[FEATURES].values

        # 5. Xử lý dự báo
        scaled_data = scaler.transform(dataset) 
        last_60_days = scaled_data[-60:]
        
        X_input = np.array([last_60_days])
        predicted_scaled = model.predict(X_input)

        # 6. Chuyển đổi giá trị dự báo về VNĐ (Trả lại hình dáng 6 cột cho scaler)
        dummy_array = np.zeros((1, len(FEATURES)))
        dummy_array[0, TARGET_INDEX] = predicted_scaled[0][0]
        predicted_price = scaler.inverse_transform(dummy_array)[0, TARGET_INDEX]

        return {
            "ticker": ticker.upper(),
            "predicted_price_vnd": float(predicted_price)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
import pandas as pd
import numpy as np
import yfinance as yf
from vnstock import stock_historical_data
from keras.models import load_model
import joblib
from datetime import datetime

# --- THÔNG SỐ CƠ BẢN ---
TIME_STEPS = 60
FEATURES = ['Open_VN', 'High_VN', 'Low_VN', 'Close_VN', 'Volume_VN', 'Close_US']
TARGET_INDEX = 3
EPOCHS = 5 # Học nhanh 5 vòng

def cap_nhat_chinh():
    print("🚀 Đang nạp mô hình gốc...")
    model = load_model('lstm_vn30_model.h5')
    scaler = joblib.load('scaler.pkl')

    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"📈 Đang kéo dữ liệu từ 2024-01-01 đến hôm nay ({today_str})...")
    
    # Lấy dữ liệu
    df_vn = stock_historical_data(symbol='HPG', start_date='2024-01-01', end_date=today_str, resolution='1D', type='stock')
    df_vn = df_vn[['time', 'open', 'high', 'low', 'close', 'volume']]
    df_vn.columns = ['Date', 'Open_VN', 'High_VN', 'Low_VN', 'Close_VN', 'Volume_VN']
    df_vn['Date'] = pd.to_datetime(df_vn['Date'])

    df_us = yf.download('^GSPC', start='2024-01-01', end=today_str, progress=False)
    if isinstance(df_us.columns, pd.MultiIndex):
        df_us = df_us['Close'].reset_index()
    else:
        df_us = df_us[['Close']].reset_index()
    df_us.columns = ['Date', 'Close_US']
    df_us['Date'] = pd.to_datetime(df_us['Date']).dt.tz_localize(None)

    # Xử lý và cho AI học
    df_merged = pd.merge(df_vn, df_us, on='Date', how='inner').ffill()
    data = df_merged[FEATURES].values
    scaled_data = scaler.transform(data) 

    X_new, y_new = [], []
    for i in range(TIME_STEPS, len(scaled_data)):
        X_new.append(scaled_data[i-TIME_STEPS:i, :])
        y_new.append(scaled_data[i, TARGET_INDEX])
    
    # Chỉ fit khi có dữ liệu mới
    if len(X_new) > 0:
        X_new, y_new = np.array(X_new), np.array(y_new)
        print("🧠 Bắt đầu cho AI học lướt...")
        model.fit(X_new, y_new, epochs=EPOCHS, batch_size=16)
        model.save('lstm_vn30_model.h5') 
        print("✅ CẬP NHẬT HOÀN TẤT! AI đã thông minh hơn.")
    else:
        print("⚠️ Chưa có đủ dữ liệu mới để cập nhật!")

if __name__ == "__main__":
    cap_nhat_chinh()
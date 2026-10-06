# VN30 LSTM — Streamlit Community Cloud

Giao diện tải dữ liệu Yahoo Finance và chạy LSTM trực tiếp trong tiến trình Streamlit.
Không cần khởi động FastAPI trên Streamlit Cloud.

## Deploy

- Repository: https://github.com/phantrinhquocbao/Do_An_2, branch `main`.
- Streamlit Cloud: Python 3.12, entrypoint `frontend/app.py`.
- Dependency chính: `requirements.txt` tại root; không cần secret/API URL.
- Chưa chạy build hoặc test local cho bản thay đổi này theo yêu cầu.

## Cấu trúc

- `frontend/app.py`: giao diện, cache dữ liệu/model, hiển thị lỗi bằng `st.error`.
- `backend/inference.py`: tải dữ liệu và suy luận dùng chung, không khởi chạy server.
- `backend/lstm_vn30_model.h5`, `backend/scaler.pkl`: model và scaler gốc.
- `backend/api.py`: API tùy chọn cho local, `/health`, `/predict/{ticker}`, `/update`.
- `backend/cap_nhat_model.py`: fine-tune thủ công; Streamlit không gọi chức năng này.
- `huggingface_space/frontend/app.py`: chuyển tiếp tới giao diện chính trong repo đầy đủ.

## Hợp đồng dữ liệu

Mã VN không có hậu tố được thêm `.VN` (ví dụ `FPT.VN`); S&P 500 dùng `^GSPC`.
Dùng `yfinance.download()`, bỏ cột dư (kể cả `Adj Close`), chuyển số và `dropna()`;
chỉ giữ `Open, High, Low, Close, Volume`, rồi ghép ngày giao dịch chung với S&P 500.
Input model giữ đúng 60 phiên x 6 cột theo thứ tự:
`Open_VN, High_VN, Low_VN, Close_VN, Volume_VN, Close_US`.
Scaler gốc được fit trên NumPy array; code giữ đúng thứ tự và kiểm tra số đặc trưng.
Giá VN dùng `auto_adjust=False`; S&P 500 giữ chuỗi Close điều chỉnh như pipeline cũ.
Model được nạp bằng Keras với `compile=False`; scaler bằng joblib, đường dẫn tính từ source.

## Giới hạn

- Yahoo có thể không cung cấp dữ liệu cho một số hoặc toàn bộ mã `.VN`, hoặc giới hạn lượt tải.
  Khi lỗi, thiếu cột hoặc thiếu 60 phiên chung, giao diện báo lỗi và không tạo dự báo giả.
  Giá VN phải có metadata currency=VND; không dùng mã trùng tên ở thị trường khác.
- Đổi nhà cung cấp không đảm bảo giá điều chỉnh/đơn vị trùng dữ liệu huấn luyện cũ;
  chưa xác minh độ chính xác sau migration. Model gốc được train trên HPG.
- Scaler được lưu với scikit-learn 1.6.1, model với Keras 3.10.0.
  Dependency không ghim phiên bản theo yêu cầu; tương thích serialization trên Cloud chưa được xác nhận.
- TensorFlow cần RAM và có thời gian cold start; cache model giúp tránh nạp lại mỗi thao tác.
- Lịch sử chỉ chứa dự báo thực trong phiên hiện tại, tối đa 100 bản ghi, không bịa MAPE.
- Notebook đã đổi nguồn dữ liệu; output cũ được giữ và đánh dấu chưa chạy lại.

## Chạy thủ công (tùy chọn)

```bash
python -m pip install -r requirements.txt
python -m streamlit run frontend/app.py
```

Backend tùy chọn: `python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000`.
Fine-tune thủ công: `python -m backend.cap_nhat_model` (ghi lại model, khởi động lại app sau đó).

Tham khảo API dữ liệu: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html

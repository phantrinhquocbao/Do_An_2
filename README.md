# 📈 Đồ Án 2: Hệ Thống Web Dự Báo Giá Cổ Phiếu VN30 Bằng Trí Tuệ Nhân Tạo (LSTM)

## 📌 Giới Thiệu Đề Tài
Dự án này là mã nguồn phục vụ cho **Đồ án 2**, tập trung vào việc xây dựng một hệ thống hoàn chỉnh (Full-stack) hỗ trợ nhà đầu tư phân tích và dự báo xu hướng giá cổ phiếu của các mã thuộc nhóm VN30. 

Hệ thống không chỉ dừng lại ở việc huấn luyện mô hình mà còn triển khai thành một **Ứng dụng Web trực quan**. Mô hình cốt lõi được sử dụng là **Mạng nơ-ron bộ nhớ dài-ngắn (Long Short-Term Memory - LSTM)**, kết hợp cùng các chỉ báo tài chính (RSI, MACD) giúp xử lý hiệu quả dữ liệu chuỗi thời gian để đưa ra các dự báo giá đóng cửa trong tương lai.

## 👥 Thông Tin Sinh Viên Thực Hiện
- **Họ và tên:** Phan Trịnh Quốc Bảo
- **Mã số sinh viên:** 222693
- **Lớp:** DH22TIN03
- **Giảng viên hướng dẫn:** ThS. Trần Văn Thiện

## 🛠 Công Nghệ & Nền Tảng
Hệ thống được thiết kế theo kiến trúc Client-Server hiện đại:
- **Ngôn ngữ chính:** Python 3.10+
- **Mô hình Trí tuệ nhân tạo (AI):** TensorFlow / Keras (LSTM)
- **Backend (API Server):** FastAPI, Uvicorn
- **Frontend (Giao diện người dùng):** Streamlit, Plotly (Vẽ biểu đồ nến tương tác)
- **Xử lý Dữ liệu:** Pandas, NumPy, Scikit-learn, yfinance, Joblib

---

## 🧠 Giải Thích Các Thành Phần Cốt Lõi

### 1. File `scaler.pkl` (Bộ Chuẩn Hóa Dữ Liệu)
Đóng vai trò cực kỳ quan trọng trong việc tiền xử lý và hậu xử lý dữ liệu:
- **Chuẩn hóa (Transform):** "Ép" các đặc trưng có thang đo chênh lệch lớn (Giá: ~100.000 VNĐ, Khối lượng: ~5.000.000, RSI: 0-100) về cùng một hệ quy chiếu [0, 1]. Điều này giúp mạng LSTM học tập các trọng số hiệu quả hơn, tránh bị thiên lệch bởi các con số quá lớn.
- **Dịch ngược (Inverse Transform):** Sau khi LSTM trả về kết quả dự báo ở dạng [0, 1], `scaler` sẽ dịch ngược con số này về lại mức giá thực tế để hiển thị trên biểu đồ.

### 2. File `lstm_vn30_model.h5` (Mô hình AI)
Đây là "bộ não" của hệ thống, chứa các trọng số đã được huấn luyện qua hàng ngàn phiên giao dịch lịch sử. Mô hình nhận đầu vào là chuỗi dữ liệu 60 ngày gần nhất để suy luận ra xu hướng giá của phiên tiếp theo.

### 3. Luồng Xử Lý Dữ Liệu (Data Flow)
1. **Frontend:** Nhận yêu cầu mã cổ phiếu từ người dùng.
2. **Backend:** Tự động lấy dữ liệu thời gian thực qua thư viện `yfinance`.
3. **Tiền xử lý:** Sử dụng `scaler.pkl` để chuẩn hóa dữ liệu đầu vào.
4. **Dự báo:** Đưa dữ liệu qua mô hình `LSTM` để tính toán giá trị dự báo.
5. **Hiển thị:** Dịch ngược giá trị về VNĐ và vẽ biểu đồ tương tác qua `Plotly`.

---

## 📂 Cấu Trúc Thư Mục
```text
DO_AN_2/
│
├── backend/                  # Mã nguồn Server (FastAPI)
│   └── api.py                # Xử lý logic API và gọi mô hình AI
│
├── frontend/                 # Mã nguồn Giao diện (Streamlit)
│   └── app.py                # Hiển thị biểu đồ và tương tác người dùng
│
├── .venv/                    # Môi trường ảo Python (Không đẩy lên GitHub)
├── lstm_vn30_model.h5        # Mô hình LSTM đã huấn luyện
├── scaler.pkl                # Bộ chuẩn hóa dữ liệu
├── CHAY_DO_AN.bat            # Script khởi động nhanh cho Windows
└── README.md                 # Hướng dẫn sử dụng

# 📈 Đồ Án 2: Hệ Thống Web Dự Báo Giá Cổ Phiếu VN30 Bằng Trí Tuệ Nhân Tạo (LSTM)

## 📌 Giới Thiệu Đề Tài
Dự án này là mã nguồn phục vụ cho **Đồ án 2**, tập trung vào việc xây dựng một hệ thống hoàn chỉnh (Full-stack) hỗ trợ nhà đầu tư phân tích và dự báo xu hướng giá cổ phiếu của các mã thuộc nhóm VN30. 

Hệ thống triển khai thành một **Ứng dụng Web trực quan** với lõi thuật toán là **Mạng nơ-ron bộ nhớ dài-ngắn (Long Short-Term Memory - LSTM)**. Điểm nổi bật của dự án là việc áp dụng phương pháp học máy đa đặc trưng (Multi-Features) kết hợp dữ liệu nội tại (OHLCV) và chỉ số vĩ mô quốc tế (S&P 500), giúp giải quyết bài toán Hồi quy (Regression) để dự báo chính xác mức giá đóng cửa T+1.

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
- **Xử lý Dữ liệu:** Pandas, NumPy, Scikit-learn, Vnstock, yfinance, Joblib

---

## 🧠 Giải Thích Các Thành Phần Cốt Lõi

### 1. File `scaler.pkl` (Bộ Chuẩn Hóa Dữ Liệu)
Đóng vai trò hạt nhân trong 파이프라인 (Pipeline) tiền xử lý và hậu xử lý dữ liệu:
- **Chuẩn hóa (Min-Max Scaling):** Nén 6 đặc trưng có biên độ chênh lệch cực lớn (Giá, Khối lượng, S&P 500) về cùng một hệ quy chiếu [0, 1]. Điều này giúp mạng LSTM hội tụ nhanh hơn và tránh hiện tượng triệt tiêu đạo hàm.
- **Dịch ngược (Inverse Transform):** Sau khi LSTM trả về kết quả dự báo ở dạng [0, 1], bộ scaler sẽ dịch ngược con số này về lại mức giá thực tế (VNĐ) để hiển thị trên giao diện.

### 2. File `lstm_vn30_model.h5` (Mô hình AI)
Đây là "bộ não" của hệ thống, được thiết lập với kiến trúc 1 lớp ẩn LSTM chứa 50 đơn vị nơ-ron, kết hợp cùng lớp Dropout 0.2 để chống Overfitting. Mô hình nhận đầu vào là ma trận dữ liệu Cửa sổ trượt (Sliding Window) kích thước 60x6 (60 ngày quá khứ x 6 đặc trưng) để suy luận ra giá đóng cửa duy nhất của phiên tiếp theo.

### 3. Luồng Xử Lý Dữ Liệu (Data Flow)
1. **Frontend:** Nhận yêu cầu mã cổ phiếu từ người dùng.
2. **Backend:** Tự động gọi API `vnstock` và `yfinance` để trích xuất 60 phiên giao dịch gần nhất.
3. **Tiền xử lý:** Sử dụng `scaler.pkl` để chuẩn hóa ma trận dữ liệu.
4. **Dự báo:** Đưa khối dữ liệu qua mô hình `LSTM` để thực thi các phép toán học sâu.
5. **Hiển thị:** Dịch ngược giá trị về VNĐ, đánh nhãn xu hướng và vẽ biểu đồ trực quan qua `Plotly`.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Bước 1: Chuẩn bị môi trường
1. Clone dự án về máy tính hoặc tải file Zip và giải nén.
2. Mở Terminal tại thư mục gốc của dự án.
3. Tạo và kích hoạt môi trường ảo (Virtual Environment):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
4. Cài đặt các thư viện cần thiết:
  pip install fastapi uvicorn streamlit plotly vnstock yfinance pandas numpy scikit-learn==1.6.1 tensorflow joblib

### Bước 2: Khởi động hệ thống
Bạn có thể chọn một trong hai cách sau:

Cách 1 (Khuyến nghị): Nhấp đúp chuột vào file CHAY_DO_AN.bat. Hệ thống sẽ tự động mở đồng thời Backend, Frontend và trình duyệt web.

Cách 2 (Thủ công): Mở 2 Terminal độc lập và chạy các lệnh sau:

Terminal 1 (Backend): uvicorn backend.api:app --reload

Terminal 2 (Frontend): streamlit run frontend/app.py

### Bước 3: Trải nghiệm và Sử dụng ứng dụng
Sau khi ứng dụng khởi chạy thành công, trình duyệt sẽ tự động điều hướng tới http://localhost:8501. Người dùng có thể trải nghiệm 5 phân hệ chức năng:

Tổng quan thị trường: Theo dõi biểu đồ nến Candlestick tương tác.

Dự báo AI: Kích hoạt mô hình LSTM để nhận mức giá mục tiêu T+1.

Phân tích chu kỳ: Xem thống kê tính mùa vụ và các tháng sinh lời tốt nhất trong 5 năm.

So sánh cổ phiếu: Đối chiếu hiệu suất tăng trưởng giữa các mã VN30 (Base 100).

Lịch sử dự báo: Xem nhật ký đối soát và sai số MAPE thực tế của hệ thống.

### 📂 Cấu Trúc Thư Mục
DO_AN_2/
│
├── backend/                  # Phía Máy chủ (Xử lý API và AI)
│   ├── api.py                # Điểm đầu vào FastAPI
│   ├── lstm_vn30_model.h5    # Trọng số mạng nơ-ron LSTM
│   └── scaler.pkl            # Bộ tham số chuẩn hóa MinMaxScaler
│
├── frontend/                 # Phía Máy khách (Giao diện)
│   └── app.py                # Script điều khiển Streamlit & Plotly
│
├── .venv/                    # Môi trường ảo (Bỏ qua trên Git)
├── .gitignore                # File cấu hình Git
├── CHAY_DO_AN.bat            # Batch script khởi động nhanh trên Windows
└── README.md                 # Tài liệu hướng dẫn dự án
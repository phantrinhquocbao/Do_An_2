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
- **Xử lý Dữ liệu:** Pandas, NumPy, Scikit-learn, Vnstock, Joblib

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
2. **Backend:** Tự động lấy dữ liệu thời gian thực qua thư viện `vnstock`.
3. **Tiền xử lý:** Sử dụng `scaler.pkl` để chuẩn hóa dữ liệu đầu vào.
4. **Dự báo:** Đưa dữ liệu qua mô hình `LSTM` để tính toán giá trị dự báo.
5. **Hiển thị:** Dịch ngược giá trị về VNĐ và vẽ biểu đồ tương tác qua `Plotly`.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Bước 1: Chuẩn bị môi trường
1. Clone dự án về máy tính hoặc tải file Zip và giải nén.
2. Mở Terminal tại thư mục gốc của dự án (`D:\Do_An_2`).
3. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   Cài đặt các thư viện cần thiết: pip install fastapi uvicorn streamlit plotly vnstock pandas numpy scikit-learn==1.6.1 tensorflow joblib
   
### Bước 2: Khởi động hệ thống
Bạn có thể chọn một trong hai cách sau:

Cách 1(Khuyến nghị): Nhấp đúp chuột vào file CHAY_DO_AN.bat. Hệ thống sẽ tự động mở đồng thời Backend, Frontend và trình duyệt web.

Cách 2(Thủ công): Mở 2 Terminal và chạy các lệnh:
Terminal 1: uvicorn backend.api:app --reload

Terminal 2: streamlit run frontend/app.py

### Bước 3: Trải nghiệm và Sử dụng ứng dụng
Sau khi ứng dụng khởi chạy thành công, trình duyệt sẽ mở địa chỉ http://localhost:8501. Người dùng thực hiện các bước sau:
1. Chọn mã cổ phiếu: Tại thanh Menu bên trái, chọn các mã chứng khoán thuộc nhóm VN30 (VD: FPT, VCB, HPG, VIC...).
2. Theo dõi biểu đồ: Hệ thống tự động tải dữ liệu lịch sử và vẽ biểu đồ nến (Candlestick) tương tác. Bạn có thể phóng to, thu nhỏ hoặc di chuyển chuột để xem giá trị tại từng thời điểm.
3. Thực hiện dự báo: Nhấn nút "Bắt đầu dự báo".
  . Backend sẽ xử lý dữ liệu qua mô hình LSTM.
  . Kết quả dự báo giá đóng cửa của phiên tiếp theo sẽ hiển thị ngay dưới biểu đồ kèm theo các chỉ số kỹ thuật liên quan.
4. Phân tích kết quả: AI cung cấp cái nhìn khách quan về xu hướng giá dựa trên dữ liệu quá khứ, giúp nhà đầu tư có thêm cơ sở tham khảo.

## 📂 Cấu Trúc Thư Mục

```text
DO_AN_2/
│
├── backend/                  # Chứa mã nguồn Server và Mô hình AI
│   ├── api.py                # Xử lý logic API, gọi mô hình AI (FastAPI)
│   ├── cap_nhat_model.py     # Script hỗ trợ cập nhật/huấn luyện lại mô hình LSTM
│   ├── code lstm.docx        # Tài liệu/Source code tham khảo về quá trình train LSTM
│   ├── lstm_vn30_model.h5    # Mô hình LSTM đã được huấn luyện
│   └── scaler.pkl            # Bộ chuẩn hóa dữ liệu đầu vào/đầu ra
│
├── frontend/                 # Chứa mã nguồn Giao diện người dùng
│   └── app.py                # Xử lý giao diện Web và biểu đồ (Streamlit)
│
├── .venv/                    # Môi trường ảo Python (Được bỏ qua khi đẩy lên GitHub)
├── .gitignore                # Khai báo các file/thư mục không đẩy lên Git
├── CHAY_DO_AN.bat            # Script Batch khởi động nhanh cả hệ thống trên Windows
├── mục tiêu.docx             # Tài liệu ghi chú mục tiêu và yêu cầu của đồ án


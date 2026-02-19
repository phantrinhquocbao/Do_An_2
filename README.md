# Đồ Án 2: Dự Báo Thị Trường Chứng Khoán (Nhóm VN30) Sử Dụng Mạng Nơ-ron LSTM

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?logo=googlecolab&logoColor=white)

## 📌 Giới thiệu đề tài
Dự án này là mã nguồn phục vụ cho **Đồ án 2**, tập trung vào việc xây dựng một hệ thống hỗ trợ đầu tư và dự báo xu hướng giá cổ phiếu của các mã thuộc nhóm VN30. Mô hình cốt lõi được sử dụng là **Mạng nơ-ron bộ nhớ dài-ngắn (Long Short-Term Memory - LSTM)**, giúp xử lý hiệu quả các dữ liệu chuỗi thời gian để đưa ra các dự báo giá đóng cửa trong tương lai.

## 👥 Thông tin sinh viên thực hiện
* **Họ và tên:** Phan Trịnh Quốc Bảo
* **Mã số sinh viên:** [222693]
* **Lớp / Khóa:** [DH22TIN03]
* **Giảng viên hướng dẫn:** [Trần Văn Thiện]

## 🛠 Công nghệ & Nền tảng
* **Ngôn ngữ:** Python
* **Mô hình học sâu:** TensorFlow / Keras
* **Xử lý & Trực quan hóa:** Pandas, NumPy, Scikit-learn, Matplotlib
* **Môi trường huấn luyện:** Google Colab (sử dụng GPU)

## 📂 Cấu trúc Repository
* `LSTM_Stock_Prediction.ipynb`: File Jupyter Notebook chứa toàn bộ mã nguồn (từ tiền xử lý dữ liệu, xây dựng mô hình đến đánh giá và dự báo).
* `data/`: Thư mục chứa tập dữ liệu lịch sử giá cổ phiếu VN30 (file `.csv`).
* `models/`: Thư mục lưu trữ mô hình LSTM đã được huấn luyện (file `.h5` hoặc `.keras`) để tải về sử dụng offline.

## 🚀 Hướng dẫn Chạy Code trên Google Colab

Vì mô hình được huấn luyện trên **Google Colab**, giảng viên không cần cài đặt môi trường phức tạp trên máy cá nhân. Chỉ cần làm theo các bước sau:

**Bước 1: Mở Notebook trên Colab**
1. Tải file `LSTM_Stock_Prediction.ipynb` trong repo này về máy.
2. Truy cập [Google Colab](https://colab.research.google.com/), chọn **Upload** và tải file vừa tải lên.

**Bước 2: Chuẩn bị dữ liệu**
1. Tải file dữ liệu `.csv` từ thư mục `data/` trong repo.
2. Trên giao diện Colab, mở tab **Files** (biểu tượng thư mục bên trái) và tải file `.csv` đó lên không gian lưu trữ của Colab (hoặc mount với Google Drive nếu code yêu cầu).

**Bước 3: Huấn luyện và Dự báo**
1. Bật GPU trên Colab: `Runtime` -> `Change runtime type` -> Chọn `T4 GPU`.
2. Chạy toàn bộ code: `Runtime` -> `Run all`.
3. Mô hình sẽ tự động tiến hành tiền xử lý, huấn luyện và in ra biểu đồ dự báo ở các cell cuối cùng.

**Bước 4: Tái sử dụng mô hình (Tùy chọn)**
Sau khi huấn luyện xong, file mô hình `.h5` sẽ được tạo ra. Có thể tải file này về máy cá nhân để chạy các script dự báo độc lập mà không cần huấn luyện lại.

## 📊 Đánh giá mô hình
* **RMSE (Root Mean Squared Error):** [Điền chỉ số]
* **MAE (Mean Absolute Error):** [Điền chỉ số]
* **MAPE (Mean Absolute Percentage Error):** [Điền chỉ số]

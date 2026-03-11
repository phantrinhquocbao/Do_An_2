import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- Cấu hình giao diện tổng quan ---
st.set_page_config(page_title="Hệ Thống Dự Báo VN30 - LSTM", page_icon="📈", layout="wide")

# --- CSS tùy chỉnh để làm đẹp giao diện ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DANH SÁCH VN30 (Khai báo trước để dùng cho Sidebar) ---
vn30_dict = {
    "ACB": "Ngân hàng TMCP Á Châu",
    "BCM": "Tổng Công ty Đầu tư và Phát triển Công nghiệp",
    "BID": "Ngân hàng TMCP Đầu tư và Phát triển VN (BIDV)",
    "BVH": "Tập đoàn Bảo Việt",
    "CTG": "Ngân hàng TMCP Công Thương VN (VietinBank)",
    "FPT": "Công ty CP FPT",
    "GAS": "Tổng Công ty Khí Việt Nam (PV GAS)",
    "GVR": "Tập đoàn Công nghiệp Cao su Việt Nam",
    "HDB": "Ngân hàng TMCP Phát triển TP.HCM (HDBank)",
    "HPG": "Tập đoàn Hòa Phát",
    "MBB": "Ngân hàng TMCP Quân Đội (MBBank)",
    "MSN": "Tập đoàn Masan",
    "MWG": "Công ty CP Đầu tư Thế Giới Di Động",
    "PLX": "Tập đoàn Xăng dầu Việt Nam (Petrolimex)",
    "POW": "Tổng Công ty Điện lực Dầu khí VN (PV Power)",
    "SAB": "Tổng Công ty CP Bia - Rượu - Nước giải khát Sài Gòn",
    "SHB": "Ngân hàng TMCP Sài Gòn - Hà Nội",
    "SSB": "Ngân hàng TMCP Đông Nam Á (SeABank)",
    "SSI": "Công ty CP Chứng khoán SSI",
    "STB": "Ngân hàng TMCP Sài Gòn Thương Tín (Sacombank)",
    "TCB": "Ngân hàng TMCP Kỹ thương VN (Techcombank)",
    "TPB": "Ngân hàng TMCP Tiên Phong (TPBank)",
    "VCB": "Ngân hàng TMCP Ngoại thương VN (Vietcombank)",
    "VHM": "Công ty CP Vinhomes",
    "VIB": "Ngân hàng TMCP Quốc tế Việt Nam",
    "VIC": "Tập đoàn Vingroup",
    "VJC": "Công ty CP Hàng không Vietjet",
    "VNM": "Công ty CP Sữa Việt Nam (Vinamilk)",
    "VPB": "Ngân hàng TMCP VN Thịnh Vượng (VPBank)",
    "VRE": "Công ty CP Vincom Retail"
}
display_options = [f"{ticker} ({name})" for ticker, name in vn30_dict.items()]

# ==========================================
# --- SIDEBAR: ĐIỀU HƯỚNG & THÔNG TIN ---
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135707.png", width=80) # Icon trang trí
    st.header("📌 Menu Chức Năng")
    
    # 1. MENU CHUYỂN TRANG
    menu = st.selectbox("Chọn trang hiển thị:", ["📈 Tổng quan thị trường", "🤖 Dự Báo Với AI (LSTM)"])
    
    st.write("---")
    
    # 2. CHỌN MÃ CỔ PHIẾU (Dùng chung cho cả 2 trang)
    st.subheader("🔍 Tra cứu mã VN30")
    selected_option = st.selectbox("Chọn mã cổ phiếu:", display_options, index=0)
    ticker_input = selected_option.split(" ")[0] 

    st.write("---")
    
    # 3. THÔNG TIN ĐỒ ÁN
    st.info(f"👨‍💻 **Thực hiện:** Phan Trịnh Quốc Bảo\n\n**Đề tài:** Dự báo VN30 ứng dụng LSTM Multi-Features")
    
    # 4. QUẢN TRỊ HỆ THỐNG
    st.subheader("⚙️ Quản trị hệ thống")
    if st.button("🔄 Cập nhật dữ liệu AI", use_container_width=True):
        with st.spinner("AI đang học thêm dữ liệu mới..."):
            try:
                res = requests.get("http://127.0.0.1:8000/update")
                if res.status_code == 200:
                    st.success("✅ Đã cập nhật kiến thức mới nhất!")
                else:
                    st.error("❌ Lỗi kết nối máy chủ cập nhật.")
            except:
                st.error("❌ Backend chưa bật hoặc lỗi kết nối.")

    st.markdown("### 💡 Giải thuật")
    st.caption("Mô hình LSTM được huấn luyện trên 6 tham số: Open, High, Low, Close, Volume (VN) và Close (S&P 500) để tăng độ chính xác vĩ mô.")

# ==========================================
# --- TRANG 1: TỔNG QUAN THỊ TRƯỜNG ---
# ==========================================
if menu == "📈 Tổng quan thị trường":
    st.title(f"📊 Phân Tích Kỹ Thuật: {selected_option}")
    st.caption("Tổng quan dữ liệu lịch sử và biến động giá thị trường hiện tại.")
    
    with st.spinner(f'Đang tải dữ liệu lịch sử cho {ticker_input}...'):
        stock = yf.Ticker(f"{ticker_input}.VN")
        df = stock.history(period="6mo")
        if df.empty:
            df = stock.history(period="6mo") # Dự phòng S&P500
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            price_change = current_price - prev_price
            change_pct = (price_change / prev_price) * 100
            
            # Hiển thị thông số cơ bản
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Giá Hiện Tại", f"{current_price:,.0f} VNĐ", f"{price_change:,.0f} ({change_pct:.2f}%)")
            col2.metric("Giá Mở Cửa", f"{df['Open'].iloc[-1]:,.0f} VNĐ")
            col3.metric("Cao Nhất Ngày", f"{df['High'].iloc[-1]:,.0f} VNĐ")
            col4.metric("Khối Lượng Giao Dịch", f"{df['Volume'].iloc[-1]:,.0f}")
            
            # Vẽ biểu đồ lịch sử (Không có điểm dự báo)
            st.subheader("Biểu Đồ Nến (Candlestick) - 6 Tháng Gần Nhất")
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Lịch sử giá"
            )])
            fig.update_layout(yaxis_title="VNĐ", height=500, template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# --- TRANG 2: DỰ BÁO VỚI AI (LSTM) ---
# ==========================================
elif menu == "🤖 Dự Báo Với AI (LSTM)":
    st.title("🤖 Dự Báo Xu Hướng Bằng Mô Hình LSTM")
    st.caption("Ứng dụng mạng nơ-ron LSTM kết hợp chỉ số chứng khoán Mỹ (S&P 500)")

    col_btn, col_info = st.columns([1, 2])

    with col_info:
        st.markdown(f"""
        **ℹ️ Thông tin mô hình đang chạy:**
        - **Mã theo dõi:** `{ticker_input}`
        - **Thị trường:** HOSE (Việt Nam) + S&P 500 (Hoa Kỳ)
        - **Cơ chế:** Nhìn lại 60 ngày giao dịch gần nhất (Time-steps: 60)
        """)
        
    with col_btn:
        st.write("") # Tạo khoảng trống để nút căn giữa cho đẹp
        predict_btn = st.button(f"🚀 Bắt Đầu Dự Báo Mã {ticker_input}", type="primary", use_container_width=True)

    st.write("---")

    # Xử lý khi nhấn nút dự báo
    if predict_btn:
        with st.spinner('⏳ Đang kết nối API và phân tích dữ liệu đa thị trường...'):
            try:
                # Gọi API lấy kết quả dự báo
                response = requests.get(f"http://127.0.0.1:8000/predict/{ticker_input}")
                data = response.json()

                if "error" in data:
                    st.error(f"🚨 Lỗi: {data['error']}")
                else:
                    predicted_price = data['predicted_price_vnd']
                    
                    # Lấy dữ liệu lịch sử để vẽ biểu đồ
                    stock = yf.Ticker(f"{ticker_input}.VN")
                    df = stock.history(period="6mo")
                    if df.empty: 
                        df = stock.history(period="6mo")

                    current_price = df['Close'].iloc[-1]
                    price_diff = predicted_price - current_price
                    diff_percent = (price_diff / current_price) * 100

                    # --- Hiển thị Metrics ---
                    st.markdown(f"### 📊 Kết Quả Dự Báo Cho Phiên Tiếp Theo ({ticker_input})")
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="Giá Đóng Cửa Gần Nhất", value=f"{current_price:,.0f} VNĐ")
                    m2.metric(label="Giá Dự Báo (AI LSTM)", value=f"{predicted_price:,.0f} VNĐ", 
                              delta=f"{price_diff:,.0f} VNĐ ({diff_percent:.2f}%)")
                    
                    # Cảnh báo xu hướng
                    if price_diff > 0:
                        m3.success("📈 Xu hướng: TĂNG")
                    else:
                        m3.error("📉 Xu hướng: GIẢM")

                    # --- Biểu đồ Plotly ---
                    st.subheader("Biểu đồ dự báo so với giá thực tế")
                    fig = go.Figure()
                    
                    # Nến Nhật
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Dữ liệu lịch sử"
                    ))
                    
                    # Điểm dự báo (Dùng Scatter)
                    fig.add_trace(go.Scatter(
                        x=[df.index[-1] + pd.Timedelta(days=1)], # Đẩy điểm dự báo sang ngày hôm sau
                        y=[predicted_price], 
                        mode='markers+text', 
                        marker=dict(color='orange', size=15, symbol='star', line=dict(width=2, color='DarkSlateGrey')),
                        name='Dự báo AI',
                        text=[f" Dự báo: {predicted_price:,.0f}"],
                        textposition="top right"
                    ))

                    fig.update_layout(yaxis_title="VNĐ", height=500, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"🚨 Lỗi kết nối hệ thống: {e}. Vui lòng kiểm tra lại Backend (FastAPI) đã chạy chưa!")
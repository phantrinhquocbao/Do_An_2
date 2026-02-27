import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go

# --- Cấu hình giao diện tổng quan ---
st.set_page_config(page_title="Hệ Thống Dự Báo VN30", page_icon="📈", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- Hiển thị thông tin đồ án tại Sidebar ---
with st.sidebar:
    st.header("📌 Thông Tin Đồ Án")
    st.write("**Môn học:** Đồ án 2")
    st.write("**Đề tài:** Xây dựng hệ thống hỗ trợ đầu tư và dự báo xu hướng cổ phiếu VN30 ứng dụng mạng nơ-ron LSTM")
    st.write("---")
    st.write("👨‍💻 **Thực hiện:**")
    st.write("- Phan Trịnh Quốc Bảo")
    st.write("---")
    st.info("💡 Hướng dẫn: Chọn mã cổ phiếu thuộc nhóm VN30 từ danh sách và bấm nút để hệ thống thực hiện dự báo.")

st.title("📈 Hệ Thống Dự Báo Xu Hướng Cổ Phiếu VN30")
st.markdown("---")

# --- DANH SÁCH VN30 CÓ KÈM TÊN CÔNG TY ---
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

# Tạo danh sách hiển thị kiểu: "HPG (Tập đoàn Hòa Phát)"
display_options = [f"{ticker} ({name})" for ticker, name in vn30_dict.items()]

col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("🔍 Tra cứu cổ phiếu")
    # Hiển thị danh sách đầy đủ tên, mặc định chọn HPG (index 9)
    selected_option = st.selectbox("Chọn mã cổ phiếu VN30 cần dự báo:", display_options, index=9)
    
    # Mẹo nhỏ: Chỉ cắt lấy cái mã (ví dụ "HPG") phía trước dấu cách để gửi cho AI
    ticker_input = selected_option.split(" ")[0] 
    
    predict_btn = st.button("🚀 Bắt Đầu Dự Báo", type="primary", use_container_width=True)

if predict_btn:
    with st.spinner('⏳ Hệ thống đang xử lý và thực hiện dự báo...'):
        try:
            # Gửi đúng cái mã "HPG" qua API
            response = requests.get(f"http://127.0.0.1:8000/predict/{ticker_input}")
            data = response.json()

            if "error" in data:
                st.error(f"🚨 Lỗi truy xuất: {data['error']}")
            else:
                predicted_price = data['predicted_price_vnd']
                
                stock = yf.Ticker(f"{ticker_input}.VN")
                df = stock.history(period="3mo")
                
                current_price = df['Close'].iloc[-1]
                price_diff = predicted_price - current_price
                diff_percent = (price_diff / current_price) * 100

                # Hiển thị Metrics phân tích
                st.subheader("📊 Kết Quả Phân Tích")
                m1, m2, m3 = st.columns(3)
                m1.metric(label="Giá Đóng Cửa Hiện Tại", value=f"{current_price:,.0f} VNĐ")
                m2.metric(label="Giá Dự Báo Tiếp Theo", value=f"{predicted_price:,.0f} VNĐ", 
                          delta=f"{price_diff:,.0f} VNĐ ({diff_percent:.2f}%)")
                m3.metric(label="Khối Lượng Giao Dịch Gần Nhất", value=f"{df['Volume'].iloc[-1]:,.0f} CP")

                st.markdown("---")
                
                # Biểu đồ kỹ thuật
                st.subheader(f"📈 Biểu Đồ Kỹ Thuật Mã Cổ Phiếu {ticker_input}")
                fig = go.Figure(data=[go.Candlestick(
                                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                name="Biến động giá", increasing_line_color='#26a69a', decreasing_line_color='#ef5350')])
                
                fig.add_trace(go.Scatter(x=[df.index[-1]], y=[predicted_price], 
                                         mode='markers', marker=dict(color='orange', size=14, symbol='star'),
                                         name='Điểm Dự Báo',
                                         hovertemplate='<b>Mức giá dự báo</b>: %{y:,.0f} VNĐ<extra></extra>'))

                fig.update_layout(xaxis_rangeslider_visible=False, height=550, margin=dict(l=0, r=0, t=30, b=0),
                                  xaxis_title="Thời Gian", yaxis_title="Mức Giá (VNĐ)", hovermode='x unified')
                fig.update_xaxes(hoverformat="%d/%m/%Y")
                
                st.plotly_chart(fig, use_container_width=True)

        except requests.exceptions.ConnectionError:
            st.error("🚨 Không thể kết nối với Backend API. Vui lòng kiểm tra lại dịch vụ.")
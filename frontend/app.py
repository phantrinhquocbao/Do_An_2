import streamlit as st
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
except Exception as e:
    st.error(str(e))
    st.stop()
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================
# 1. CẤU HÌNH TRANG & CSS (LIGHT THEME - NHƯ ẢNH)
# ==========================================
st.set_page_config(page_title="Hệ thống dự báo VN30", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

try:
    from backend.inference import load_data, load_features, load_artifacts, predict_price
except Exception as e:
    st.error(str(e))
    st.stop()


@st.cache_resource
def get_model_and_scaler():
    return load_artifacts()


@st.cache_data(ttl=3600)
def cached_stock_data(ticker, start_date, end_date):
    return load_data(ticker, start_date, end_date)


@st.cache_data(ttl=3600)
def cached_features(ticker, start_date, end_date):
    return load_features(ticker, start_date, end_date)


def get_stock_data(ticker, period="6mo"):
    try:
        end = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").normalize().tz_localize(None)
        offset = {"6mo": pd.DateOffset(months=6), "1y": pd.DateOffset(years=1),
                  "5y": pd.DateOffset(years=5)}[period]
        start = end - offset
        return cached_stock_data(ticker, str(start.date()), str(end.date()))
    except Exception as e:
        st.error(str(e))
        return pd.DataFrame()


def main():
    # Tùy chỉnh CSS để làm các thẻ Metric giống y hệt trong ảnh (khung trắng, viền nhạt, bo góc)
    st.markdown("""
        <style>
        div[data-testid="metric-container"] {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
        }
        /* Đổi màu chữ label của metric thành xám nhạt cho tinh tế */
        div[data-testid="stMetricLabel"] > div {
            color: #555555 !important;
            font-size: 14px !important;
        }
        /* Màu số liệu chính */
        div[data-testid="stMetricValue"] {
            color: #212529 !important;
        }
        /* Chỉnh nút bấm */
        .stButton>button {
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE)
    # ==========================================
    if 'pred_p' not in st.session_state:
        st.session_state.pred_p = None

    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []

    # Danh sách VN30 kèm tên đầy đủ để hiển thị đẹp như ảnh
    vn30_dict = {
        "ACB": "Ngân hàng TMCP Á Châu", "BID": "BIDV", "CTG": "VietinBank", "FPT": "FPT Group",
        "GAS": "PV GAS", "HPG": "Tập đoàn Hòa Phát", "MBB": "MBBank", "MSN": "Tập đoàn Masan",
        "MWG": "Thế Giới Di Động", "SSI": "Chứng khoán SSI", "STB": "Sacombank",
        "TCB": "Techcombank", "VCB": "Vietcombank", "VHM": "Vinhomes",
        "VIC": "Tập đoàn Vingroup", "VNM": "Vinamilk", "VPB": "VPBank"
    }

    # ==========================================
    # 3. SIDEBAR (BỐ CỤC Y HỆT ẢNH CHỤP)
    # ==========================================
    with st.sidebar:
        # Avatar giả lập
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>🧑‍💼</h1>", unsafe_allow_html=True)

        st.markdown("### 📌 Menu Chức Năng")
        st.caption("Chọn trang hiển thị:")
        menu = st.selectbox("Menu", [
            "📈 Tổng quan thị trường",
            "🤖 Dự Báo Với AI (LSTM)",
            "📊 Phân tích chu kỳ",
            "⚖️ So sánh cổ phiếu",
            "📜 Lịch sử dự báo"
        ], label_visibility="collapsed")

        st.write("---")
        st.markdown("### 🔍 Tra cứu mã VN30")
        st.caption("Chọn mã cổ phiếu:")

        # Format hiển thị selectbox: "ACB (Ngân hàng TMCP Á Châu)"
        options = [f"{k} ({v})" for k, v in vn30_dict.items()]
        selected_option = st.selectbox("Ticker", options, label_visibility="collapsed")
        ticker_symbol = selected_option.split(" ")[0] # Lấy mỗi chữ "ACB"
        ticker_name = vn30_dict[ticker_symbol]

        # Reset dự báo khi đổi mã
        if 'current_ticker' not in st.session_state or st.session_state.current_ticker != ticker_symbol:
            st.session_state.pred_p = None
            st.session_state.current_ticker = ticker_symbol

        st.write("---")

        # Khối thông tin sinh viên
        st.info("👨‍💻 **Thực hiện:** Phan Trịnh Quốc Bảo\n\n📘 **Đề tài:** Dự báo VN30 ứng dụng LSTM Multi-Features")

        # --- ĐỂ NÚT CẬP NHẬT Ở DƯỚI CÙNG CHO ĐẸP ---
        st.markdown("### ⚙️ Quản trị hệ thống")
        if st.button("🔄 Tải lại dữ liệu thị trường", use_container_width=True):
            cached_stock_data.clear()
            cached_features.clear()
            st.session_state.pred_p = None
            st.rerun()

        st.markdown("### 💡 Giải thuật")
        st.caption("Mô hình LSTM được huấn luyện trên 6 tham số: Open, High, Low, Close, Volume (VN) và Close (S&P 500) để tăng độ chính xác vĩ mô.")
    # ==========================================
    # 4. LOGIC LẤY DỮ LIỆU
    # ==========================================
    df = get_stock_data(ticker_symbol)

    # ==========================================
    # 5. HIỂN THỊ CÁC TRANG THEO MENU
    # ==========================================

    if len(df) >= 2:
        current_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]

        # ------------------------------------------
        # TRANG 1: TỔNG QUAN THỊ TRƯỜNG (Y HỆT ẢNH)
        # ------------------------------------------
        if menu == "📈 Tổng quan thị trường":
            st.header(f"📊 Phân Tích Kỹ Thuật: {ticker_symbol} ({ticker_name})")
            st.caption("Tổng quan dữ liệu lịch sử và biến động giá thị trường hiện tại.")
            st.write("") # Tạo khoảng trống

            # 4 Cột Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Giá Hiện Tại", f"{current_p:,.0f} VNĐ", f"{(current_p - prev_p):+,.0f} ({((current_p-prev_p)/prev_p*100):+.2f}%)")
            m2.metric("Giá Mở Cửa", f"{df['Open'].iloc[-1]:,.0f} VNĐ")
            m3.metric("Cao Nhất Ngày", f"{df['High'].iloc[-1]:,.0f} VNĐ")
            m4.metric("Khối Lượng Giao Dịch", f"{df['Volume'].iloc[-1]:,.0f}")

            st.write("---")
            st.subheader("Biểu Đồ Nến (Candlestick) - 6 Tháng Gần Nhất")

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
            # Nến
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Giá", increasing_line_color='#089981', decreasing_line_color='#F23645' # Màu chuẩn TradingView
            ), row=1, col=1)
            # Khối lượng
            colors = ['#089981' if r['Close'] >= r['Open'] else '#F23645' for _, r in df.iterrows()]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

            # Sử dụng nền sáng plotly_white
            fig.update_layout(
                template="plotly_white", height=600, xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------
        # TRANG 2: DỰ BÁO VỚI AI
        # ------------------------------------------
        elif menu == "🤖 Dự Báo Với AI (LSTM)":
            st.header(f"🤖 Kích Hoạt AI Dự Báo: {ticker_symbol}")
            st.caption("Sử dụng mạng nơ-ron LSTM để suy luận giá đóng cửa cho phiên giao dịch kế tiếp.")

            col_chart, col_order = st.columns([3, 1])

            with col_order:
                st.markdown("### ⚙️ Bảng Điều Khiển")
                amount = st.number_input("Số lượng mua giả định (cp):", min_value=100, value=1000, step=100)
                btn_predict = st.button("🚀 CHẠY MÔ HÌNH DỰ BÁO", type="primary", use_container_width=True)

                if btn_predict:
                    st.session_state.pred_p = None
                    try:
                        with st.spinner("Đang tải dữ liệu, model và tính toán 60 phiên..."):
                            end = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").normalize().tz_localize(None)
                            start = end - pd.Timedelta(days=365)
                            features = cached_features(ticker_symbol, str(start.date()), str(end.date()))
                            if features.index[-1] != df.index[-1]:
                                raise ValueError("S&P 500 và mã VN chưa có dữ liệu cùng phiên gần nhất; chưa thể dự báo T+1.")
                            model, scaler = get_model_and_scaler()
                            predicted_price = predict_price(features, model, scaler)
                            st.session_state.pred_p = predicted_price
                            st.session_state.pred_date = features.index[-1]
                            st.session_state.prediction_history.append({
                                "Thời gian truy vấn": pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").isoformat(),
                                "Mã CK": ticker_symbol,
                                "Phiên dữ liệu cuối": str(features.index[-1].date()),
                                "Giá AI dự báo (VNĐ)": predicted_price,
                            })
                            st.session_state.prediction_history = st.session_state.prediction_history[-100:]
                    except Exception as e:
                        st.error(str(e))

                if st.session_state.pred_p:
                    p_val = st.session_state.pred_p
                    st.caption(f"Phiên dữ liệu cuối: {st.session_state.pred_date.date()}")
                    # ... (phần dưới này ông giữ nguyên)
                    p_diff = p_val - current_p
                    st.write("---")
                    st.metric("Giá mục tiêu T+1", f"{p_val:,.0f} VNĐ", f"{p_diff:+,.0f} ({(p_diff/current_p*100):+.2f}%)")
                    if p_diff > 0:
                        st.success(f"Dự tính lợi nhuận: +{(p_diff * amount):,.0f} VNĐ")
                    else:
                        st.error(f"Dự tính rủi ro: {(p_diff * amount):,.0f} VNĐ")

            with col_chart:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name="Giá Thực Tế", line=dict(color='#2962FF', width=2)))

                if st.session_state.pred_p:
                    next_date = st.session_state.pred_date + pd.offsets.BDay(1)
                    fig.add_trace(go.Scatter(
                        x=[next_date], y=[st.session_state.pred_p], mode='markers+text',
                        marker=dict(color='#FF9800', size=15, symbol='star'),
                        name='Dự báo T+1', text=[f"{st.session_state.pred_p:,.0f}"], textposition="top center"
                    ))
                    fig.add_trace(go.Scatter(
                        x=[df.index[-1], next_date], y=[current_p, st.session_state.pred_p],
                        mode='lines', line=dict(color='#FF9800', width=2, dash='dash'), showlegend=False
                    ))

                fig.update_layout(template="plotly_white", height=500, title="Biểu đồ đường (Line Chart) đối chiếu dự báo")
                st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------
        # TRANG 3: PHÂN TÍCH CHU KỲ (BẢN DỄ HIỂU CHO NGƯỜI NGHIỆP DƯ)
        # ------------------------------------------
        elif menu == "📊 Phân tích chu kỳ":
            st.header(f"📊 Lịch Sử Tăng/Giảm Theo Tháng: {ticker_symbol}")
            st.caption("Thống kê xem trong quá khứ, cổ phiếu này thường tăng hay giảm vào những tháng nào trong năm, giúp bạn chọn thời điểm mua/bán tốt nhất.")

            # Lấy dữ liệu 5 năm để có cái nhìn tổng quan đủ dài
            df_long = get_stock_data(ticker_symbol, period="5y")

            if not df_long.empty:
                try:
                    # Tính lợi nhuận từng tháng
                    monthly_data = df_long['Close'].resample('ME').last()
                except:
                    monthly_data = df_long['Close'].resample('M').last()

                monthly_returns = monthly_data.pct_change() * 100
                monthly_returns = monthly_returns.dropna()
                if monthly_returns.empty:
                    st.error("Chưa đủ dữ liệu tháng để phân tích chu kỳ.")
                    st.stop()

                # Tạo DataFrame gom nhóm theo 12 tháng (1 -> 12)
                df_analysis = pd.DataFrame({'Return': monthly_returns})
                df_analysis['Month'] = df_analysis.index.month

                # Tính trung bình mức tăng/giảm của từng tháng trong 5 năm qua
                monthly_avg = df_analysis.groupby('Month')['Return'].mean()

                # Đổi tên tháng cho dễ đọc
                month_names = [f"Tháng {i}" for i in monthly_avg.index]

                # Tìm tháng tốt nhất và tệ nhất để in ra kết luận
                best_month = monthly_avg.idxmax()
                worst_month = monthly_avg.idxmin()

                # --- KHU VỰC KẾT LUẬN TỰ ĐỘNG (Dành cho người không rành xem biểu đồ) ---
                st.info(f"💡 **AI Tổng hợp nhanh (Dữ liệu 5 năm qua):**\n\n"
                        f"- 🌟 **Tháng tốt nhất để mua:** **Tháng {best_month}** (Trung bình tăng trưởng cao nhất: **{monthly_avg[best_month]:+.2f}%**).\n"
                        f"- ⚠️ **Tháng nên cẩn trọng:** **Tháng {worst_month}** (Thường có xu hướng giảm: **{monthly_avg[worst_month]:+.2f}%**).")

                st.write("---")

                # --- VẼ BIỂU ĐỒ CỘT SIÊU DỄ NHÌN ---
                st.subheader("Biểu đồ hiệu suất trung bình 12 tháng")

                fig_bar = go.Figure(go.Bar(
                    x=month_names,
                    y=monthly_avg.values,
                    text=[f"{val:+.1f}%" for val in monthly_avg.values],
                    textposition='auto',
                    marker_color=['#089981' if val > 0 else '#F23645' for val in monthly_avg.values]
                ))

                fig_bar.update_layout(
                    template="plotly_white",
                    height=450,
                    xaxis_title="Các tháng trong năm",
                    yaxis_title="Mức tăng/giảm trung bình (%)",
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown("*Lưu ý: Thống kê dựa trên dữ liệu quá khứ, mang tính chất tham khảo cho tính chu kỳ (seasonality) của thị trường.*")

        # ------------------------------------------
        # TRANG 4: SO SÁNH CỔ PHIẾU
        # ------------------------------------------
        elif menu == "⚖️ So sánh cổ phiếu":
            st.header("⚖️ So Sánh Tương Quan Hiệu Suất")
            st.caption("Đưa các mã chứng khoán về cùng hệ quy chiếu (Base 100) để đánh giá sức mạnh tương đối.")

            selected_tickers = st.multiselect("Chọn các mã VN30 để so sánh:", list(vn30_dict.keys()), default=list(dict.fromkeys([ticker_symbol, "FPT", "HPG"])))

            if selected_tickers:
                fig_comp = go.Figure()
                for t in selected_tickers:
                    data = get_stock_data(t, "1y")
                    if not data.empty:
                        normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                        fig_comp.add_trace(go.Scatter(x=normalized_price.index, y=normalized_price, mode='lines', name=t))

                fig_comp.update_layout(template="plotly_white", height=500, yaxis_title="Điểm hiệu suất (Base 100)")
                st.plotly_chart(fig_comp, use_container_width=True)

        # ------------------------------------------
        # TRANG 5: LỊCH SỬ DỰ BÁO
        # ------------------------------------------
        elif menu == "📜 Lịch sử dự báo":
            st.header("📜 Nhật Ký Đối Soát Hệ Thống")
            st.caption("Tối đa 100 dự báo thực trong phiên hiện tại; chưa đối soát giá tương lai.")
            if st.session_state.prediction_history:
                st.dataframe(pd.DataFrame(st.session_state.prediction_history), use_container_width=True)
            else:
                st.info("Chưa có dự báo trong phiên này.")

    else:
        st.error("Cần ít nhất hai phiên dữ liệu hợp lệ từ Yahoo Finance để hiển thị mã này.")


try:
    main()
except Exception as e:
    st.session_state.pred_p = None
    st.error(str(e))

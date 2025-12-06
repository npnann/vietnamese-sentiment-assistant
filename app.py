import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Dict

from modules.sentiment import load_sentiment_model, classify
from modules.preprocessing import preprocess
from modules.storage import save_result, get_history, get_total_count, get_filtered_count
from modules.validation import validate_input

SENTIMENT_CONFIG = {
    'POSITIVE': {
        'color': 'var(--md-positive)',
        'bg_color': 'var(--md-positive-container)',
        'icon': '😊',
        'label': 'Tích cực'
    },
    'NEUTRAL': {
        'color': 'var(--md-neutral)',
        'bg_color': 'var(--md-neutral-container)',
        'icon': '😐',
        'label': 'Trung tính'
    },
    'NEGATIVE': {
        'color': 'var(--md-negative)',
        'bg_color': 'var(--md-negative-container)',
        'icon': '😔',
        'label': 'Tiêu cực'
    }
}

SENTIMENT_FILTER_MAP = {
    "Tích cực": "POSITIVE",
    "Trung tính": "NEUTRAL",
    "Tiêu cực": "NEGATIVE"
}

@st.cache_data(ttl=3600)
def load_css_content():
    try:
        with open("assets/css/style.css", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def load_assets():
    css_content = load_css_content()
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            width: 100%;
            margin-bottom: unset !important; 
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            flex: 1;
        }
        
        .stTabs [data-baseweb="tab"] > div:first-child {
            width: 100%;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Trợ lý phân loại cảm xúc tiếng Việt",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    load_assets()
    
    st.markdown("""
    <div class="md-card md-card-elevated" style="margin-bottom: 24px; background: linear-gradient(135deg, var(--md-primary), var(--md-secondary));">
        <div style="text-align: center; color: white; padding: 32px 24px;">
            <h1 style="margin: 0; font-size: 32px; font-weight: 600;">🤖 Vietnamese Sentiment Assistant</h1>
            <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 16px;">Phân loại cảm xúc văn bản tiếng Việt</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Đang tải model..."):
        model = load_sentiment_model()
    
    tab1, tab2 = st.tabs(["🤖 Phân loại", "📜 Lịch sử"])
    
    with tab1:
        classification_tab()
    
    with tab2:
        history_tab()


def classification_tab():
    st.markdown('<h2 style="color: var(--md-primary); margin-bottom: 24px;">📝 Phân loại cảm xúc</h2>', unsafe_allow_html=True)
    
    with st.form(key="classification_form", clear_on_submit=True):
        user_input = st.text_area(
            "Nhập văn bản tiếng Việt:",
            placeholder="Nhập câu hoặc đoạn văn bản tiếng Việt để phân loại cảm xúc...",
            height=120,
            max_chars=50,
            key="sentiment_input",
            help="Nhập văn bản từ 5-50 ký tự. Có thể bao gồm viết tắt, thiếu dấu, và emoji."
        )
    
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🔍 Phân loại cảm xúc", 
                type="primary", 
                width='stretch', 
                use_container_width=True
            )
    if submitted:
        if user_input:
            char_count = len(user_input)
            st.markdown(f"""
            <div style="text-align: right; font-size: 12px; color: var(--md-on-surface-variant); margin-top: -8px; margin-bottom: 16px;">
                {char_count}/50 ký tự
            </div>
            """, unsafe_allow_html=True)

            is_valid, validation_msg = validate_input(user_input)

            if not is_valid:
                st.markdown(f"""
                <div class="md-card" style="background: var(--md-error-container); color: var(--md-on-error-container); border-left: 4px solid var(--md-error);">
                    <strong>⚠️ Lỗi:</strong> {validation_msg}
                </div>
                """, unsafe_allow_html=True)
                return
            try:
                processed_text = preprocess(user_input)
                result = classify(processed_text)
                save_result(result)
                
                display_result(result)                    
            except RuntimeError as e:
                st.markdown(f"""
                <div class="md-card" style="background: var(--md-error-container); color: var(--md-on-error-container); border-left: 4px solid var(--md-error);">
                    <strong>❌ Có lỗi xảy ra:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)


def display_result(result: Dict[str, Any]):
    config = SENTIMENT_CONFIG.get(result['sentiment'], SENTIMENT_CONFIG['NEUTRAL']).copy()
    config['text'] = result['text']
    
    st.markdown(f"""
    <div class="md-sentiment-result md-sentiment-result-{result['sentiment'].lower()}" style="display: flex; align-items: center;">
        <div style="flex: 1; text-align: center; border-right: 1px solid {config['color']};">
            <div class="md-sentiment-text" style="font-size: 18px; word-wrap: break-word;">{config['text']}</div>
        </div>
        <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
            <span class="md-sentiment-emoji">{config['icon']}</span>
            <span class="md-sentiment-label" style="font-size: 16px; font-weight: 600; color: {config['color']}; margin-left: 8px;">{config['label']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def history_tab():
    st.markdown('<h2 style="color: var(--md-primary); margin-bottom: 24px;">📜 Lịch sử phân loại</h2>', unsafe_allow_html=True)
    
    search_query = st.text_input("🔍 Tìm kiếm trong lịch sử:", key="history_search", placeholder="Nhập văn bản cần tìm...")
    
    filter_option = st.selectbox(
        "Lọc theo cảm xúc:",
        ["Tất cả", "Tích cực", "Trung tính", "Tiêu cực"],
        key="sentiment_filter"
    )
    
    sentiment_filter_value = SENTIMENT_FILTER_MAP.get(filter_option) if filter_option != "Tất cả" else None
    search_query_value = search_query.strip() if search_query else None
    
    records_per_page = 10
    if sentiment_filter_value or search_query_value:
        total_records = get_filtered_count(
            search_query=search_query_value,
            sentiment_filter=sentiment_filter_value
        )
    else:
        total_records = get_total_count()
    total_pages = (total_records + records_per_page - 1) // records_per_page
    
    if total_pages == 0:
        st.markdown("""
        <div class="md-card" style="text-align: center; padding: 40px 24px; background: var(--md-surface-container);">
            <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
            <h3 style="color: var(--md-on-surface-variant); margin-bottom: 8px;">Lịch sử trống</h3>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Trang trước", disabled=st.session_state.current_page <= 1):
            st.session_state.current_page = max(1, st.session_state.current_page - 1)
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; color: var(--md-on-surface-variant);'>
            Trang {st.session_state.current_page}/{total_pages}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Trang sau →", disabled=st.session_state.current_page >= total_pages):
            st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
            st.rerun()
    
    offset = (st.session_state.current_page - 1) * records_per_page
    
    with st.spinner("Đang tải lịch sử..."):
        history_data = get_history(
            limit=records_per_page, 
            offset=offset,
            search_query=search_query_value,
            sentiment_filter=sentiment_filter_value
        )
    
    if not history_data:
        st.markdown("""
        <div class="md-card" style="text-align: center; padding: 40px 24px; background: var(--md-surface-container);">
            <p style="color: var(--md-on-surface-variant);">Không tìm thấy kết quả phù hợp.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown('<h3 style="color: var(--md-primary); margin-bottom: 16px;">📊 Lịch sử phân loại gần đây</h3>', unsafe_allow_html=True)
    
    table_data = []
    for i, record in enumerate(history_data):
        timestamp = datetime.fromisoformat(record['timestamp']).strftime('%H:%M %d/%m/%Y')
        confidence = f"{record['confidence']:.1%}"
        
        emoji = SENTIMENT_CONFIG.get(record['sentiment'], {}).get('icon', '❓')
        text = record['text']
        if len(text) > 30:
            text = text[:27] + "..."
        
        table_data.append({
            'STT': i + 1,
            'Văn bản': text,
            'Cảm xúc': f"{emoji} {record['sentiment']}",
            'Độ tin cậy': confidence,
            'Thời gian': timestamp
        })
    
    df = pd.DataFrame(table_data)
    
    st.markdown("""
    <style>
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: var(--md-elevation-level1) !important;
    }
    
    .dataframe th {
        background-color: var(--md-surface-variant) !important;
        color: var(--md-on-surface-variant) !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 16px !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .dataframe td {
        padding: 16px !important;
        border-top: 1px solid var(--md-surface-variant) !important;
        color: var(--md-on-surface) !important;
    }
    
    .dataframe tr:hover {
        background-color: var(--md-surface-container) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.info("Không tìm thấy kết quả phù hợp với bộ lọc.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="md-metrics-container">', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="md-metric-card">
                <div class="md-metric-value">{total_records}</div>
                <div class="md-metric-label">Tổng số bản ghi</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            positive_count = sum(1 for r in history_data if r['sentiment'] == 'POSITIVE')
            st.markdown(f"""
            <div class="md-metric-card">
                <div class="md-metric-value" style="color: var(--md-positive);">{positive_count}</div>
                <div class="md-metric-label">😊 Tích cực</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            negative_count = sum(1 for r in history_data if r['sentiment'] == 'NEGATIVE')
            st.markdown(f"""
            <div class="md-metric-card">
                <div class="md-metric-value" style="color: var(--md-negative);">{negative_count}</div>
                <div class="md-metric-label">😔 Tiêu cực</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    


if __name__ == "__main__":
    main()
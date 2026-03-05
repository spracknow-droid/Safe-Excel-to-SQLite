import streamlit as st

def sidebar_query_editor():
    st.sidebar.subheader("⌨️ SQL Query Editor")
    query = st.sidebar.text_area("SQL 문을 입력하세요", height=200)
    run_btn = st.sidebar.button("실행하기", use_container_width=True)
    return query, run_btn

def data_viewer_ui(tables, views):
    """라디오 버튼과 셀렉트 박스 조합 UI"""
    st.markdown("### 📊 Data Browser")
    c1, c2 = st.columns([1, 2])
    with c1:
        target_type = st.radio("유형", ["Table", "View"], horizontal=True)
    with c2:
        options = tables if target_type == "Table" else views
        selected = st.selectbox(f"{target_type} 선택", options)
    return target_type, selected

def display_stats(tables, views):
    """현황 요약 대시보드"""
    c1, c2 = st.columns(2)
    c1.metric("물리 테이블", f"{len(tables)}개")
    c2.metric("가상 뷰(View)", f"{len(views)}개")

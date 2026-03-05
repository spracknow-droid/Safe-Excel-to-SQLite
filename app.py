import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="SQLite Web Viewer", layout="wide")

st.title("📂 SQLite 파일 웹 뷰어")
st.info("왼쪽 사이드바에서 .db 또는 .sqlite 파일을 업로드하세요.")

# 1. 파일 업로드 (사이드바)
uploaded_file = st.sidebar.file_uploader("DB 파일 선택", type=["db", "sqlite", "sqlite3"])

if uploaded_file is not None:
    # 업로드된 파일을 임시로 로컬에 저장 (sqlite3 연결을 위함)
    temp_db = "temp_user_db.db"
    with open(temp_db, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 2. DB 연결 및 테이블 목록 가져오기
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            st.warning("데이터베이스 내에 테이블이 존재하지 않습니다.")
        else:
            # 3. 테이블 선택 UI
            selected_table = st.sidebar.selectbox("조회할 테이블 선택", tables)
            
            # 4. 데이터 불러오기 (Pandas)
            df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)

            # 5. 상단 지표 (자유자재 활용 예시)
            col1, col2 = st.columns(2)
            col1.metric("총 행 수 (Rows)", len(df))
            col2.metric("컬럼 수 (Columns)", len(df.columns))

            # 6. 데이터 출력 및 편집 모드
            st.subheader(f"📊 {selected_table} 데이터 테이블")
            st.data_editor(df, use_container_width=True) # 엑셀처럼 수정 가능

            # 7. 간단한 시각화 추가 (숫자 데이터가 있을 경우)
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(num_cols) >= 1:
                st.subheader("📈 퀵 시각화")
                target_col = st.selectbox("차트로 볼 컬럼 선택", num_cols)
                st.line_chart(df[target_col])

        conn.close()

    except Exception as e:
        st.error(f"에러 발생: {e}")
    
    finally:
        # 사용이 끝난 후 임시 파일 삭제 (선택 사항)
        if os.path.exists(temp_db):
            pass 
else:
    st.write("---")
    st.caption("파일을 업로드하면 여기에 데이터가 나타납니다.")

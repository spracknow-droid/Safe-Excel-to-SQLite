import streamlit as st
import pandas as pd
import sqlite3
import io
import os

st.set_page_config(page_title="Safe Excel to SQLite (Date Support)", layout="wide")

st.title("🛡️ 데이터 무결성 보장 Excel to SQLite")
st.info("데이터 훼손을 막기 위해 모든 데이터를 먼저 '문자열'로 읽어온 후, 지정하신 타입으로 DB에 저장합니다.")

# 1. 파일 업로드 (사이드바)
uploaded_file = st.sidebar.file_uploader("엑셀 파일 업로드", type=["xlsx", "xls"])

if uploaded_file:
    # [중요] dtype=str 옵션으로 모든 데이터를 원본 문자열 그대로 읽어옵니다.
    df = pd.read_excel(uploaded_file, dtype=str)
    
    st.subheader("📋 원본 데이터 미리보기 (Raw String)")
    st.dataframe(df.head(5))

    st.divider()

    # 2. 설정 영역
    st.subheader("⚙️ 테이블 및 컬럼 타입 설정")
    table_name = st.text_input("테이블 이름", value="my_table")
    
    # DATE 타입을 추가한 설정 옵션
    type_options = {
        "문자열 (TEXT)": "TEXT", 
        "정수 (INTEGER)": "INTEGER", 
        "실수 (REAL)": "REAL",
        "날짜 (DATE)": "DATE"
    }
    
    selected_types = {}
    cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        with cols[i % 4]:
            selected_types[col_name] = st.selectbox(
                f"컬럼: {col_name}",
                options=list(type_options.keys()),
                key=f"type_{col_name}"
            )

    # 3. DB 변환 및 생성
    if st.button("🚀 데이터 타입 적용 및 DB 생성"):
        try:
            # 변환용 데이터프레임 복사
            process_df = df.copy()
            
            # 날짜 형식 처리 (YYYY-MM-DD)
            for col, t_name in selected_types.items():
                if t_name == "날짜 (DATE)":
                    # pd.to_datetime을 이용해 시분초를 제거하고 날짜만 추출
                    process_df[col] = pd.to_datetime(process_df[col]).dt.strftime('%Y-%m-%d')

            db_filename = "converted_data.db"
            
            # 기존 파일 제거
            if os.path.exists(db_filename):
                os.remove(db_filename)

            conn = sqlite3.connect(db_filename)
            cursor = conn.cursor()

            # [핵심] 사용자가 정한 타입으로 테이블 스키마 생성
            cols_def = ", ".join([f'"{c}" {type_options[selected_types[c]]}' for c in process_df.columns])
            create_query = f'CREATE TABLE "{table_name}" ({cols_def})'
            cursor.execute(create_query)

            # [핵심] 데이터를 튜플 형태로 변환하여 INSERT
            placeholders = ", ".join(["?" for _ in process_df.columns])
            insert_query = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
            
            # 데이터프레임의 모든 값을 리스트 내 튜플로 변환 (NaN은 None으로 처리)
            data_to_insert = process_df.where(pd.notnull(process_df), None).values.tolist()
            cursor.executemany(insert_query, data_to_insert)
            
            conn.commit()
            conn.close()

            with open(db_filename, "rb") as f:
                st.success(f"✅ 변환 완료! '{table_name}' 테이블이 생성되었습니다.")
                st.download_button(
                    label="💾 생성된 SQLite DB 다운로드",
                    data=f,
                    file_name=f"{table_name}.db",
                    mime="application/x-sqlite3"
                )

        except Exception as e:
            st.error(f"변환 중 오류 발생: {e}")
            st.warning("팁: 날짜 컬럼에 잘못된 날짜 형식이 있거나, 숫자로 지정한 컬럼에 문자가 들어있는지 확인해 보세요.")

else:
    st.write("사이드바에서 파일을 업로드해 주세요.")

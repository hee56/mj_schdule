import streamlit as st
from datetime import datetime
import pandas as pd
import os
from utils.data_manager import load_data, save_data, backup_data
from pages.checklist import render_checklist
from pages.calendar import render_calendar
from pages.analysis import show_data_analysis

def ensure_directories():
    """필요한 디렉토리 생성"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('backup', exist_ok=True)

def main():
    # 페이지 기본 설정
    st.set_page_config(
        page_title="메이지님의 첫 번째 streamlit app",
        page_icon="🐭",
        layout="wide"
    )

    # 디렉토리 생성
    ensure_directories()

    # 데이터 초기화
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    # 사이드바 
    with st.sidebar:
        st.title('Hello')
        
        menu = st.selectbox(
            '메뉴 선택',
            ['메인 페이지', '체크리스트', '데이터 분석']
        )

    # 메인 컨텐츠
    if menu == '메인 페이지':
        st.title('메이지님의 첫 번째 streamlit app')
        
        st.markdown("### Welcome~")
        st.markdown("페이지를 시작합니다!!")
        st.markdown("이메일: @usja.hs.kr")

    elif menu == '체크리스트':
        selected_date = st.date_input("날짜 선택", datetime.now())
        render_checklist(selected_date)
        st.markdown("---")
        render_calendar(selected_date)
        
        # 데이터 저장
        save_data(st.session_state.data)

    elif menu == '데이터 분석':
        st.subheader('데이터 백업 및 분석')
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button('데이터 백업'):
                backup_data()
                st.success('데이터가 백업되었습니다!')
        
        with col2:
            st.markdown("데이터를 백업하고 학습 현황을 분석할 수 있습니다.")
        
        show_data_analysis()

if __name__ == "__main__":
    main()

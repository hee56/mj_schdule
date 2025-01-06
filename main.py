import streamlit as st
from datetime import datetime
import pandas as pd
import pytz
import os
from utils.data_manager import load_data, save_data, backup_data
from pages.checklist import render_checklist
from pages.calendar import render_calendar
from pages.analysis import show_data_analysis

# 서울 시간대 설정
seoul_tz = pytz.timezone('Asia/Seoul')

# 현재 서울 시간 가져오기
current_time = datetime.now(seoul_tz).strftime('%H:%M')

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
        st.title('메뉴')
        
        view_option = st.radio(
            "보기 선택",
            ["데이터 분석"]
        )
        
        if st.button('데이터 백업'):
            backup_data()
            st.success('데이터가 백업되었습니다!')

    # 타이틀 표시
    st.title('일일 학습 체크리스트')
    
    # 날짜 선택을 위한 열 생성
    date_col1, date_col2 = st.columns([2, 3])
    with date_col1:
        selected_date = st.date_input("날짜 선택", datetime.now(seoul_tz))

    # 메인 컨텐츠 (체크리스트)
    render_checklist(selected_date)
    
    # 데이터 저장
    save_data(st.session_state.data)
    
    # 캘린더는 항상 체크리스트 아래에 표시
    st.markdown("---")
    render_calendar(selected_date)
    
    # 데이터 분석 선택시 표시
    if view_option == "데이터 분석":
        st.markdown("---")
        show_data_analysis()

if __name__ == "__main__":
    main()

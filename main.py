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

def init_session_state(activity_type):
    """세션 스테이트 초기화"""
    if f'new_{activity_type}_hours' not in st.session_state:
        st.session_state[f'new_{activity_type}_hours'] = 0.0
    if f'new_{activity_type}_memo' not in st.session_state:
        st.session_state[f'new_{activity_type}_memo'] = ''

def render_activity_section(activity_type, date_key, title):
    """활동(학습/휴식) 섹션 렌더링"""
    init_session_state(activity_type)
    
    if date_key not in st.session_state.data['activities']:
        st.session_state.data['activities'][date_key] = {'study': [], 'break': []}
    
    activities = st.session_state.data['activities'][date_key][activity_type]
    total_hours = sum(record['hours'] for record in activities)
    
    if activities:
        st.write(f"오늘의 {title} 기록:")
        for record in activities:
            st.markdown(f"- {format_time_display(record['hours'])}: {record['memo']} ({record['timestamp']})")
        
        st.markdown(f"**총 {title} 시간: {format_time_display(total_hours)}**")
        st.markdown("---")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("-30분", key=f"minus_{activity_type}"):
            if st.session_state[f'new_{activity_type}_hours'] >= 0.5:
                st.session_state[f'new_{activity_type}_hours'] -= 0.5
                st.rerun()

    with col2:
        if st.button("+30분", key=f"plus_{activity_type}"):
            st.session_state[f'new_{activity_type}_hours'] += 0.5
            st.rerun()

    with col3:
        if st.button("+5분", key=f"plus5_{activity_type}"):
            st.session_state[f'new_{activity_type}_hours'] += 5 / 60
            st.rerun()

    with col4:
        st.markdown(f"**선택된 시간: {format_time_display(st.session_state[f'new_{activity_type}_hours'])}**")

    memo = st.text_input(f'{title} 내용', key=f'memo_{activity_type}')

    if st.button(f'{title} 시간 추가', key=f'add_{activity_type}'):
        if st.session_state[f'new_{activity_type}_hours'] > 0:
            st.session_state.data['activities'][date_key][activity_type].append({
                'hours': st.session_state[f'new_{activity_type}_hours'],
                'memo': memo,
                'timestamp': datetime.now(seoul_tz).strftime('%H:%M')
            })
            st.session_state[f'new_{activity_type}_hours'] = 0.0
            st.rerun()

    if st.button(f'오늘 {title} 기록 초기화', key=f'reset_{activity_type}'):
        st.session_state.data['activities'][date_key][activity_type] = []
        st.session_state[f'new_{activity_type}_hours'] = 0.0
        st.rerun()
    
    return total_hours

def render_checklist(selected_date):
    date_key = selected_date.strftime("%Y-%m-%d")
    # ... (기존 render_checklist 구현)
    # datetime.now() -> datetime.now(seoul_tz).strftime('%H:%M')로 변경 필요

def ensure_directories():
    """필요한 디렉토리 생성"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('backup', exist_ok=True)

def main():
    st.set_page_config(
        page_title="메이지님의 첫 번째 streamlit app",
        page_icon="🐭",
        layout="wide"
    )

    ensure_directories()

    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    st.title('일일 학습 체크리스트')
    selected_date = st.date_input("날짜 선택", datetime.now(seoul_tz))

    with st.sidebar:
        st.title('메뉴')
        view_option = st.radio("보기 선택", ["캘린더", "데이터 분석"])
        if st.button('데이터 백업'):
            backup_data()
            st.success('데이터가 백업되었습니다!')

    render_checklist(selected_date)
    save_data(st.session_state.data)
    
    st.markdown("---")
    if view_option == "캘린더":
        render_calendar(selected_date)
    else:
        show_data_analysis()

if __name__ == "__main__":
    main()

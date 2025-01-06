import streamlit as st
import calendar
from datetime import datetime, timedelta
from utils.data_manager import format_time_display

def adjust_day_order(days):
    """월요일부터 시작하는 날짜를 수요일부터 시작하도록 조정"""
    # 앞의 3일(월,화,수)을 뒤로 이동
    return days[2:] + days[:2]

def create_calendar_grid(selected_date):
    c = calendar.monthcalendar(selected_date.year, selected_date.month)
    
    # 수요일부터 시작하는 달력으로 조정
    first_day_weekday = selected_date.replace(day=1).weekday()  # 0=월요일, ..., 6=일요일
    
    # 첫 주가 비어있으면 제거
    if all(day == 0 for day in c[0]):
        c.pop(0)
    
    return c

def render_calendar(selected_date):
    st.markdown("### 월간 기록")
    month_matrix = create_calendar_grid(selected_date)
    
    # 요일 순서 조정 (수요일부터 시작)
    weekdays = adjust_day_order(['수', '목', '금', '토', '일', '월', '화'])
    
    # 요일 헤더
    cols = st.columns(7)
    for idx, day in enumerate(weekdays):
        with cols[idx]:
            # 일요일 (원래 인덱스에서 2일 이동)
            if day == '일':
                color = '#ff4b4b'
            # 토요일 (원래 인덱스에서 2일 이동)
            elif day == '토':
                color = '#4b7bff'
            else:
                color = '#ffffff'
            st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)

    # 달력 내용 표시
    for week in month_matrix:
        cols = st.columns(7)
        week = adjust_day_order(week)  # 요일 순서 조정
        
        for idx, day in enumerate(week):
            with cols[idx]:
                if day != 0:
                    date_str = f"{selected_date.year}-{selected_date.month:02d}-{day:02d}"
                    study_records = st.session_state.data['activities'].get(date_str, {}).get('study', [])
                    break_records = st.session_state.data['activities'].get(date_str, {}).get('break', [])
                    total_study = sum(record['hours'] for record in study_records)
                    total_break = sum(record['hours'] for record in break_records)
                    has_review = date_str in st.session_state.data['reviews']
                    
                    # 날짜 표시 (요일에 따른 색상)
                    if weekdays[idx] == '일':
                        color = '#ff4b4b'
                    elif weekdays[idx] == '토':
                        color = '#4b7bff'
                    else:
                        color = '#ffffff'
                        
                    st.markdown(
                        f"<div style='text-align: center;'>"
                        f"<div style='color: {color}; font-weight: bold; font-size: 1.1em;'>{day}</div>"
                        f"{'<div style=\"color: #ffffff; font-size: 0.9em;\">공부: ' + format_time_display(total_study) + '</div>' if total_study > 0 else ''}"
                        f"{'<div style=\"color: #ffffff; font-size: 0.9em;\">휴식: ' + format_time_display(total_break) + '</div>' if total_break > 0 else ''}"
                        f"{'<div style=\"color: #ffffff;\">📝</div>' if has_review else ''}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write("")

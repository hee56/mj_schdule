import streamlit as st
import calendar
from utils.data_manager import format_time_display

def create_calendar_grid(selected_date):
    month_matrix = []
    week = []
    first_day = calendar.monthrange(selected_date.year, selected_date.month)[0]
    days_in_month = calendar.monthrange(selected_date.year, selected_date.month)[1]
    
    for i in range(first_day):
        week.append(None)
        
    for day in range(1, days_in_month + 1):
        week.append(day)
        if len(week) == 7:
            month_matrix.append(week)
            week = []
            
    if week:
        while len(week) < 7:
            week.append(None)
        month_matrix.append(week)
        
    return month_matrix

def render_calendar(selected_date):
    st.markdown("""
    <style>
    .calendar-header {
        font-weight: bold;
        text-align: center;
        padding: 5px;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 월간 기록")
    month_matrix = create_calendar_grid(selected_date)
    
    # 요일 헤더
    cols = st.columns(7)
    weekdays = ['일', '월', '화', '수', '목', '금', '토']
    for idx, day in enumerate(weekdays):
        with cols[idx]:
            if idx == 0:  # 일요일
                st.markdown(f"<div class='calendar-header' style='color: #ff4b4b;'>{day}</div>", unsafe_allow_html=True)
            elif idx == 6:  # 토요일
                st.markdown(f"<div class='calendar-header' style='color: #4b7bff;'>{day}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='calendar-header'>{day}</div>", unsafe_allow_html=True)

    # 달력 그리드 생성
    for week in month_matrix:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            with cols[idx]:
                if day is not None:
                    date_str = f"{selected_date.year}-{selected_date.month:02d}-{day:02d}"
                    study_records = st.session_state.data['activities'].get(date_str, {}).get('study', [])
                    break_records = st.session_state.data['activities'].get(date_str, {}).get('break', [])
                    total_study = sum(record['hours'] for record in study_records)
                    total_break = sum(record['hours'] for record in break_records)
                    has_review = date_str in st.session_state.data['reviews']
                    
                    # 날짜 색상 설정
                    if idx == 0:  # 일요일
                        day_color = '#ff4b4b'
                    elif idx == 6:  # 토요일
                        day_color = '#4b7bff'
                    else:
                        day_color = '#ffffff'
                    
                    # 학습과 휴식 시간 정보 준비
                    study_info = f"<div style='color: #ffffff; font-size: 0.9em;'>공부: {format_time_display(total_study)}</div>" if total_study > 0 else ""
                    break_info = f"<div style='color: #ffffff; font-size: 0.9em;'>휴식: {format_time_display(total_break)}</div>" if total_break > 0 else ""
                    review_icon = f"<div style='color: #ffffff;'>📝</div>" if has_review else ""
                    
                    # HTML 마크다운으로 렌더링
                    st.markdown(
                        f"<div style='text-align: center;'>"
                        f"<div style='color: {day_color}; font-weight: bold; font-size: 1.1em;'>{day}</div>"
                        f"{study_info}{break_info}{review_icon}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write("")  # 빈 칸

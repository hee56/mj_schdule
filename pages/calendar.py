import streamlit as st
import calendar
from utils.data_manager import format_time_display

def create_calendar_grid(selected_date):
    from datetime import datetime, timedelta
    
    # 해당 월의 1일 구하기
    first_day = selected_date.replace(day=1)
    
    # 해당 월의 마지막 날짜 구하기
    if selected_date.month == 12:
        last_day = selected_date.replace(year=selected_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = selected_date.replace(month=selected_date.month + 1, day=1) - timedelta(days=1)
    
    # 달력에 표시할 첫 날짜 구하기 (해당 월 1일이 속한 주의 일요일)
    calendar_start = first_day - timedelta(days=first_day.weekday() + 1)
    if first_day.weekday() == 6:  # 1일이 일요일인 경우
        calendar_start = first_day
    
    # 날짜 채우기
    month_matrix = []
    current_date = calendar_start
    
    # 6주 분량의 날짜 생성
    for week in range(6):
        week_dates = []
        for i in range(7):  # 일요일부터 토요일까지
            # 현재 월에 속하는 날짜만 표시, 나머지는 None
            if current_date.month == selected_date.month:
                week_dates.append(current_date.day)
            else:
                week_dates.append(None)
            current_date += timedelta(days=1)
        month_matrix.append(week_dates)
        
        # 마지막 날짜를 넘어갔고, 현재 주가 비어있다면 중단
        if current_date > last_day and all(d is None for d in week_dates):
            month_matrix.pop()
            break
            
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
    .calendar-day {
        text-align: center;
        padding: 5px;
    }
    .calendar-content {
        margin-top: 2px;
        font-size: 0.9em;
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
            color = '#ff4b4b' if idx == 0 else '#4b7bff' if idx == 6 else '#ffffff'
            st.markdown(f"<div class='calendar-header' style='color: {color};'>{day}</div>", unsafe_allow_html=True)

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
                    day_color = '#ff4b4b' if idx == 0 else '#4b7bff' if idx == 6 else '#ffffff'
                    
                    # HTML 마크다운으로 렌더링
                    content = [
                        f"<div class='calendar-day'>",
                        f"<div style='color: {day_color}; font-weight: bold; font-size: 1.1em;'>{day}</div>"
                    ]
                    
                    if total_study > 0:
                        content.append(f"<div class='calendar-content' style='color: #ffffff;'>공부: {format_time_display(total_study)}</div>")
                    if total_break > 0:
                        content.append(f"<div class='calendar-content' style='color: #ffffff;'>휴식: {format_time_display(total_break)}</div>")
                    if has_review:
                        content.append(f"<div class='calendar-content' style='color: #ffffff;'>📝</div>")
                    
                    content.append("</div>")
                    st.markdown("".join(content), unsafe_allow_html=True)
                else:
                    st.write("")

import streamlit as st
import calendar
from utils.data_manager import format_time_display

def create_calendar_grid(selected_date):
    # 달력 객체 생성
    cal = calendar.Calendar()
    
    # 해당 월의 모든 날짜를 가져옴
    month_dates = list(cal.itermonthdays2(selected_date.year, selected_date.month))
    
    # 주 단위로 데이터 구성
    month_matrix = []
    week = []
    
    # 월의 첫 날 구하기
    first_day = month_dates[0][1]  # (day, weekday)의 weekday
    
    # 첫 주 빈칸 채우기
    for i in range(first_day):
        week.append(None)
    
    # 나머지 날짜 채우기
    for day, weekday in month_dates:
        if day != 0:  # 실제 날짜인 경우만 추가
            week.append(day)
            if len(week) == 7:
                month_matrix.append(week)
                week = []
    
    # 마지막 주 남은 공간 채우기
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

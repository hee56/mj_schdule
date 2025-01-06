import streamlit as st
from datetime import datetime, timedelta
from utils.data_manager import format_time_display

def create_calendar_grid(selected_date):
    # 해당 월의 첫 날과 마지막 날 구하기
    first_day = selected_date.replace(day=1)
    if selected_date.month == 12:
        last_day = selected_date.replace(year=selected_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = selected_date.replace(month=selected_date.month + 1, day=1) - timedelta(days=1)

    # 요일 계산 수정
    first_weekday = calendar.weekday(first_day.year, first_day.month, first_day.day)

    # 달력 시작 날짜 수정
    start_date = first_day - timedelta(days=first_weekday - 6)

    
    # 달력 생성
    calendar_days = []
    current_date = start_date
    
    while len(calendar_days) < 42:  # 6주 분량
        week = []
        for _ in range(7):
            if current_date.month == selected_date.month:
                week.append(current_date.day)
            else:
                week.append(None)
            current_date += timedelta(days=1)
        calendar_days.append(week)
        
        # 마지막 주가 모두 다음 달이면 중단
        if current_date > last_day and all(d is None for d in week):
            calendar_days.pop()
            break
            
    return calendar_days

def render_calendar(selected_date):
    st.markdown("""
    <style>
    .calendar-header {
        font-weight: bold;
        text-align: center;
        padding: 5px;
        margin-bottom: 10px;
    }
    .calendar-cell {
        text-align: center;
        padding: 8px;
        min-height: 80px;
    }
    .day-number {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    .activity-info {
        font-size: 0.9em;
        margin-top: 3px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 월 표시
    st.markdown(f"### {selected_date.year}년 {selected_date.month}월")
    
    # 요일 헤더
    cols = st.columns(7)
    weekdays = ['일', '월', '화', '수', '목', '금', '토']
    for idx, day in enumerate(weekdays):
        with cols[idx]:
            color = '#ff4b4b' if idx == 0 else '#4b7bff' if idx == 6 else '#ffffff'
            st.markdown(
                f"<div class='calendar-header' style='color: {color};'>{day}</div>",
                unsafe_allow_html=True
            )

    # 달력 그리드 생성
    # 달력 그리드 생성
    calendar_days = create_calendar_grid(selected_date)
    for week in calendar_days:
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
                    color = '#ff4b4b' if idx == 0 else '#4b7bff' if idx == 6 else '#ffffff'
                    
                    html_content = [
                        f"<div class='calendar-cell'>",
                        f"<div class='day-number' style='color: {color};'>{day}</div>"
                    ]
                    '''
                    if total_study > 0:
                        html_content.append(
                            f"<div class='activity-info' style='color: #ffffff;'>"
                            f"공부: {format_time_display(total_study)}</div>"
                        )
                    if total_break > 0:
                        html_content.append(
                            f"<div class='activity-info' style='color: #ffffff;'>"
                            f"휴식: {format_time_display(total_break)}</div>"
                        )
                    if has_review:
                        html_content.append(
                            "<div class='activity-info' style='color: #ffffff;'>📝</div>"
                        )
                    '''
                    for record in study_records:
                        html_content.append(
                            f"<div class='activity-info' style='color: #ffffff;'>"
                            f"공부: {record['subject']} ({record['hours']}시간)</div>"
                        )
                        
                    html_content.append("</div>")
                    st.markdown("".join(html_content), unsafe_allow_html=True)
                else:
                    st.write("")

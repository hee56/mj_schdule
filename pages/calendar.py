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

                    # Iterate through all study records and display information
                    for record in study_records:
                        html_content.append(
                            f"<div class='activity-info' style='color: #ffffff;'>"
                            f"공부: {record['subject']} ({record['hours']}시간)</div>"
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

                    html_content.append("</div>")
                    st.markdown("".join(html_content), unsafe_allow_html=True)
                else:
                    st.write("")

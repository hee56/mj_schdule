import streamlit as st
import json
import os
from datetime import datetime, timedelta
import calendar

def load_data():
    if os.path.exists('checklist_data.json'):
        with open('checklist_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 데이터 구조 마이그레이션
            if 'activities' not in data:
                migrated_data = {
                    'activities': {},
                    'checklist': data.get('checklist', {}),
                    'reviews': {}
                }
                
                # 학습 시간 마이그레이션
                for date, records in data.get('study_hours', {}).items():
                    if date not in migrated_data['activities']:
                        migrated_data['activities'][date] = {'study': [], 'break': []}
                    
                    if isinstance(records, (int, float)):
                        migrated_data['activities'][date]['study'] = [{
                            'hours': float(records),
                            'memo': '이전 기록',
                            'timestamp': '00:00'
                        }]
                    else:
                        migrated_data['activities'][date]['study'] = records

                # 총평 마이그레이션
                for date, review in data.get('daily_reviews', {}).items():
                    migrated_data['reviews'][date] = {
                        'content': review,
                        'timestamp': '00:00'
                    }
                
                return migrated_data
            return data
    
    return {
        'activities': {},
        'checklist': {},
        'reviews': {}
    }

def save_data(data):
    with open('checklist_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_day_type(date):
    day = date.weekday()
    if day == 6:  # Sunday
        return 'sunday'
    elif day == 5:  # Saturday
        return 'saturday'
    elif day in [0, 2, 4]:  # Monday, Wednesday, Friday
        return 'mwf'
    else:  # Tuesday, Thursday
        return 'tt'

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

def format_time_display(total_hours):
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    if minutes > 0:
        return f"{hours}시간 {minutes}분"
    return f"{hours}시간"

def render_activity_section(activity_type, date_key, title):
    if date_key not in st.session_state.data['activities']:
        st.session_state.data['activities'][date_key] = {'study': [], 'break': []}
    
    activities = st.session_state.data['activities'][date_key][activity_type]
    total_hours = sum(record['hours'] for record in activities)
    
    if activities:
        st.write(f"오늘의 {title} 기록:")
        for idx, record in enumerate(activities):
            st.markdown(f"- {format_time_display(record['hours'])}: {record['memo']} ({record['timestamp']})")
        
        st.markdown(f"**총 {title} 시간: {format_time_display(total_hours)}**")
        st.markdown("---")

    col1, col2 = st.columns([1, 2])
    with col1:
        new_hours = st.number_input(
            f'{title} 시간',
            min_value=0.0,
            max_value=24.0,
            value=0.0,
            step=0.5,
            key=f'new_{activity_type}_hours'
        )
    with col2:
        memo = st.text_input(
            f'{title} 내용',
            key=f'new_{activity_type}_memo'
        )

    if st.button(f'{title} 시간 추가', key=f'add_{activity_type}'):
        if new_hours > 0:
            st.session_state.data['activities'][date_key][activity_type].append({
                'hours': new_hours,
                'memo': memo,
                'timestamp': datetime.now().strftime('%H:%M')
            })
            st.rerun()

    if st.button(f'오늘 {title} 기록 초기화', key=f'reset_{activity_type}'):
        st.session_state.data['activities'][date_key][activity_type] = []
        st.rerun()
    
    return total_hours

def main():
    st.title('일일 학습 체크리스트')

    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    left_col, right_col = st.columns([4, 6])

    selected_date = st.date_input("날짜 선택", datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

    with left_col:
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
                        
                        st.markdown(f"""
                            <div style='text-align: center;'>
                                <div style='color: {day_color}; font-weight: bold; font-size: 1.1em;'>
                                    {day}
                                </div>
                                {f"<div style='color: #ffffff; font-size: 0.9em;'>공부: {format_time_display(total_study)}</div>" if total_study > 0 else ""}
                                {f"<div style='color: #ffffff; font-size: 0.9em;'>휴식: {format_time_display(total_break)}</div>" if total_break > 0 else ""}
                                {f"<div style='color: #ffffff;'>📝</div>" if has_review else ""}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.write("")  # 빈 칸

    with right_col:
        schedules = {
            'mwf': [
                {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
                {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
                {'id': 'class', 'label': '수업 (3:30)', 'time': '3:30'},
                {'id': 'meal', 'label': '식사 및 휴식 (3:00↓)', 'time': '3:00'},
                {'id': 'tkd', 'label': '태권도 (1:30↓)', 'time': '1:30'},
                {'id': 'study', 'label': '학습 (8:00↑)', 'time': '8:00'},
                {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
                {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
            ],
            'tt': [
                {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
                {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
                {'id': 'class', 'label': '수업 (3:30)', 'time': '3:30'},
                {'id': 'meal', 'label': '식사 및 휴식 (3:00↓)', 'time': '3:00'},
                {'id': 'study', 'label': '학습 (9:30↑)', 'time': '9:30'},
                {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
                {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
            ],
            'saturday': [
                {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
                {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
                {'id': 'class', 'label': '수업 (10:30)', 'time': '10:30'},
                {'id': 'meal', 'label': '식사 및 휴식 (3:30)', 'time': '3:30'},
                {'id': 'study', 'label': '학습 (3:00)', 'time': '3:00'},
                {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
                {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
            ],
            'sunday': [
                {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
                {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
                {'id': 'meal', 'label': '식사 및 휴식 (4:00)', 'time': '4:00'},
                {'id': 'study', 'label': '학습 (11:00↑)', 'time': '11:00'},
                {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
            ]
        }

        target_study_hours = {
            'mwf': 8,
            'tt': 9.5,
            'saturday': 3,
            'sunday': 11
        }

        day_type = get_day_type(selected_date)
        current_schedule = schedules[day_type]

        st.subheader('오늘의 체크리스트')
        
        if date_key not in st.session_state.data['checklist']:
            st.session_state.data['checklist'][date_key] = {}

        for item in current_schedule:
            checked = st.checkbox(
                f"{item['label']} ({item['time']})",
                key=f"{date_key}_{item['id']}",
                value=st.session_state.data['checklist'][date_key].get(item['id'], False)
            )
            st.session_state.data['checklist'][date_key][item['id']] = checked

        st.subheader('학습 시간 기록')
        study_hours = render_activity_section('study', date_key, '학습')

        st.subheader('휴식 시간 기록')
        break_hours = render_activity_section('break', date_key, '휴식')

        target_hours = target_study_hours[day_type]
        if study_hours >= target_hours:
            evaluation = 'GOOD'
            color = 'green'
        elif study_hours > 0:
            evaluation = 'BAD'
            color = 'red'
        else:
            evaluation = '미입력'
            color = 'gray'

        st.markdown(f"**학습 평가:** :{color}[{evaluation}]")

        # 일일 총평
        st.subheader('오늘의 총평')
        review_content = ""
        if date_key in st.session_state.data['reviews']:
            review_content = st.session_state.data['reviews'][date_key]['content']
        
        daily_review = st.text_area(
            "오늘 하루를 돌아보며...",
            value=review_content,
            height=150,
            placeholder="오늘의 성과, 부족한 점, 내일의 계획 등을 기록해보세요."
        )

        if daily_review:
            st.session_state.data['reviews'][date_key] = {
                'content': daily_review,
                'timestamp': datetime.now().strftime('%H:%M')
            }

    # 데이터 저장
    save_data(st.session_state.data)

    # 데이터 백업 다운로드 버튼
    if st.button('데이터 백업'):
        json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
        st.download_button(
            label="JSON 파일 다운로드",
            data=json_str,
            file_name="checklist_backup.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()

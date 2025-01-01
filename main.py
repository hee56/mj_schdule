import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar

def load_data():
    data = {
        'activities': {},
        'checklist': {},
        'reviews': {}
    }
    
    # 체크리스트 데이터 로드
    if os.path.exists('checklist_data.csv'):
        checklist_df = pd.read_csv('checklist_data.csv')
        for _, row in checklist_df.iterrows():
            date = row['date']
            if date not in data['checklist']:
                data['checklist'][date] = {}
            data['checklist'][date][row['item_id']] = row['checked']

    # 활동(학습/휴식) 데이터 로드
    if os.path.exists('activities_data.csv'):
        activities_df = pd.read_csv('activities_data.csv')
        for _, row in activities_df.iterrows():
            date = row['date']
            if date not in data['activities']:
                data['activities'][date] = {'study': [], 'break': []}
            activity_type = row['activity_type']
            data['activities'][date][activity_type].append({
                'hours': float(row['hours']),
                'memo': row['memo'],
                'timestamp': row['timestamp']
            })

    # 총평 데이터 로드
    if os.path.exists('reviews_data.csv'):
        reviews_df = pd.read_csv('reviews_data.csv')
        for _, row in reviews_df.iterrows():
            date = row['date']
            data['reviews'][date] = {
                'content': row['content'],
                'timestamp': row['timestamp']
            }
    
    return data

def save_data(data):
    # 체크리스트 데이터 저장
    checklist_records = []
    for date, items in data['checklist'].items():
        for item_id, checked in items.items():
            checklist_records.append({
                'date': date,
                'item_id': item_id,
                'checked': checked
            })
    
    if checklist_records:
        checklist_df = pd.DataFrame(checklist_records)
        checklist_df.to_csv('checklist_data.csv', index=False)

    # 활동(학습/휴식) 데이터 저장
    activity_records = []
    for date, activities in data['activities'].items():
        for activity_type, records in activities.items():
            for record in records:
                activity_records.append({
                    'date': date,
                    'activity_type': activity_type,
                    'hours': record['hours'],
                    'memo': record['memo'],
                    'timestamp': record['timestamp']
                })
    
    if activity_records:
        activities_df = pd.DataFrame(activity_records)
        activities_df.to_csv('activities_data.csv', index=False)

    # 총평 데이터 저장
    review_records = []
    for date, review in data['reviews'].items():
        review_records.append({
            'date': date,
            'content': review['content'],
            'timestamp': review['timestamp']
        })
    
    if review_records:
        reviews_df = pd.DataFrame(review_records)
        reviews_df.to_csv('reviews_data.csv', index=False)

def backup_data():
    # 백업 디렉토리 생성
    if not os.path.exists('backup'):
        os.makedirs('backup')
        
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists('checklist_data.csv'):
        df = pd.read_csv('checklist_data.csv')
        df.to_csv(f'backup/checklist_data_{backup_time}.csv', index=False)
    
    if os.path.exists('activities_data.csv'):
        df = pd.read_csv('activities_data.csv')
        df.to_csv(f'backup/activities_data_{backup_time}.csv', index=False)
    
    if os.path.exists('reviews_data.csv'):
        df = pd.read_csv('reviews_data.csv')
        df.to_csv(f'backup/reviews_data_{backup_time}.csv', index=False)

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

    # 시간 선택을 위한 session state 초기화
    if f'new_{activity_type}_hours' not in st.session_state:
        st.session_state[f'new_{activity_type}_hours'] = 0.0

    # 시간 조절 버튼과 표시
    col1, col2, col3 = st.columns([1, 1, 2])
    
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
        st.markdown(f"**선택된 시간: {format_time_display(st.session_state[f'new_{activity_type}_hours'])}**")

    memo = st.text_input(
        f'{title} 내용',
        key=f'new_{activity_type}_memo'
    )

    if st.button(f'{title} 시간 추가', key=f'add_{activity_type}'):
        if st.session_state[f'new_{activity_type}_hours'] > 0:
            st.session_state.data['activities'][date_key][activity_type].append({
                'hours': st.session_state[f'new_{activity_type}_hours'],
                'memo': memo,
                'timestamp': datetime.now().strftime('%H:%M')
            })
            st.session_state[f'new_{activity_type}_hours'] = 0.0  # 시간 초기화
            st.rerun()

    if st.button(f'오늘 {title} 기록 초기화', key=f'reset_{activity_type}'):
        st.session_state.data['activities'][date_key][activity_type] = []
        st.session_state[f'new_{activity_type}_hours'] = 0.0  # 시간 초기화
        st.rerun()
    
    return total_hours

def render_calendar(selected_date, data):
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
                    study_records = data['activities'].get(date_str, {}).get('study', [])
                    break_records = data['activities'].get(date_str, {}).get('break', [])
                    total_study = sum(record['hours'] for record in study_records)
                    total_break = sum(record['hours'] for record in break_records)
                    has_review = date_str in data['reviews']
                    
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

def main():
    st.title('일일 학습 체크리스트')

    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    selected_date = st.date_input("날짜 선택", datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

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

    # 메인 컨텐츠 영역
    st.subheader('오늘의 체크리스트')
    
    if date_key not in st.session_state.data['checklist']:
        st.session_state.data['checklist'][date_key] = {}

    # 체크리스트 표시
    for item in current_schedule:
        checked = st.checkbox(
            f"{item['label']} ({item['time']})",
            key=f"{date_key}_{item['id']}",
            value=st.session_state.data['checklist'][date_key].get(item['id'], False)
        )
        st.session_state.data['checklist'][date_key][item['id']] = checked

    # 학습 시간 섹션과 평가
    study_col1, study_col2 = st.columns([3, 1])
    with study_col1:
        st.subheader('학습 시간 기록')
        study_hours = render_activity_section('study', date_key, '학습')
    with study_col2:
        st.markdown("##### 학습 평가")
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
        st.markdown(f":{color}[{evaluation}]")

    # 휴식 시간 섹션과 평가
    break_col1, break_col2 = st.columns([3, 1])
    with break_col1:
        st.subheader('휴식 시간 기록')
        break_hours = render_activity_section('break', date_key, '휴식')
    with break_col2:
        st.markdown("##### 휴식 평가")
        if break_hours > 3:
            evaluation = 'EMERGENCY'
            color = 'red'
        elif break_hours > 2.5:
            evaluation = 'WARNING'
            color = 'orange'
        else:
            evaluation = 'NORMAL'
            color = 'green'
        st.markdown(f":{color}[{evaluation}]")

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

    # 캘린더 표시
    st.markdown("---")  # 구분선 추가
    render_calendar(selected_date, st.session_state.data)

    # 데이터 저장
    save_data(st.session_state.data)

    # 데이터 백업 버튼
    if st.button('데이터 백업'):
        backup_data()
        st.success('데이터가 백업되었습니다!')

if __name__ == "__main__":
    main()

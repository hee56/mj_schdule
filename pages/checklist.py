import streamlit as st
from datetime import datetime
from utils.data_manager import get_day_type, format_time_display

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
            st.session_state[f'new_{activity_type}_hours'] = 0.0
            st.rerun()

    if st.button(f'오늘 {title} 기록 초기화', key=f'reset_{activity_type}'):
        st.session_state.data['activities'][date_key][activity_type] = []
        st.session_state[f'new_{activity_type}_hours'] = 0.0
        st.rerun()
    
    return total_hours

def render_checklist(selected_date):
    date_key = selected_date.strftime("%Y-%m-%d")
    
    # 스케줄 정의
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

    # 체크리스트
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

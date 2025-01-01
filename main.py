import streamlit as st
import json
import os
from datetime import datetime, timedelta
import calendar

def load_data():
    if os.path.exists('checklist_data.json'):
        with open('checklist_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 이전 형식의 study_hours 데이터를 새로운 형식으로 변환
            if 'study_hours' in data:
                converted_hours = {}
                for date, hours in data['study_hours'].items():
                    if isinstance(hours, (int, float)):
                        converted_hours[date] = [
                            {'hours': float(hours), 'memo': '이전 기록', 'timestamp': '00:00'}
                        ]
                    else:
                        converted_hours[date] = hours
                data['study_hours'] = converted_hours
            
            return data
    return {
        'checklist': {},
        'study_hours': {},
        'daily_reviews': {}
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
    
    # 첫 주 빈 칸 채우기
    for i in range(first_day):
        week.append(None)
        
    # 날짜 채우기
    for day in range(1, days_in_month + 1):
        week.append(day)
        if len(week) == 7:
            month_matrix.append(week)
            week = []
            
    # 마지막 주 빈 칸 채우기
    if week:
        while len(week) < 7:
            week.append(None)
        month_matrix.append(week)
        
    return month_matrix

def main():
    st.title('일일 학습 체크리스트')

    # 데이터 로드
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    # 화면을 왼쪽과 오른쪽으로 분할
    left_col, right_col = st.columns([4, 6])  # 비율 4:6으로 분할

    # 날짜 선택 (상단에 배치)
    selected_date = st.date_input("날짜 선택", datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

    with left_col:
        st.markdown("### 월간 기록")
        month_matrix = create_calendar_grid(selected_date)
        
        # 요일 헤더
        cols = st.columns(7)
        weekdays = ['일', '월', '화', '수', '목', '금', '토']
        for idx, day in enumerate(weekdays):
            with cols[idx]:
                if idx == 0:  # 일요일
                    st.markdown(f"<h5 style='text-align: center; color: red;'>{day}</h5>", unsafe_allow_html=True)
                elif idx == 6:  # 토요일
                    st.markdown(f"<h5 style='text-align: center; color: blue;'>{day}</h5>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h5 style='text-align: center;'>{day}</h5>", unsafe_allow_html=True)

        # 달력 그리드 생성
        for week in month_matrix:
            cols = st.columns(7)
            for idx, day in enumerate(week):
                with cols[idx]:
                    if day is not None:
                        date_str = f"{selected_date.year}-{selected_date.month:02d}-{day:02d}"
                        study_records = st.session_state.data['study_hours'].get(date_str, [])
                        if isinstance(study_records, (int, float)):
                            study_records = [{'hours': float(study_records), 'memo': '이전 기록', 'timestamp': '00:00'}]
                            st.session_state.data['study_hours'][date_str] = study_records
                        total_hours = sum(record['hours'] for record in study_records)
                        has_review = st.session_state.data['daily_reviews'].get(date_str, '')
                        
                        # 날짜 색상 설정
                        if idx == 0:  # 일요일
                            st.markdown(f"<h4 style='text-align: center; color: red;'>{day}</h4>", unsafe_allow_html=True)
                        elif idx == 6:  # 토요일
                            st.markdown(f"<h4 style='text-align: center; color: blue;'>{day}</h4>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h4 style='text-align: center;'>{day}</h4>", unsafe_allow_html=True)
                        
                        # 학습 시간 표시
                        if total_hours > 0:
                            st.markdown(f"<p style='text-align: center;'>{total_hours:.1f}시간</p>", unsafe_allow_html=True)
                            
                        # 총평 아이콘 표시
                        if has_review:
                            st.markdown("<p style='text-align: center;'>📝</p>", unsafe_allow_html=True)
                    else:
                        st.write("")  # 빈 칸

    with right_col:
        # 요일별 스케줄 정의
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

        # 체크리스트 표시
        day_type = get_day_type(selected_date)
        current_schedule = schedules[day_type]

        st.subheader('오늘의 체크리스트')
        
        # 데이터 초기화
        if date_key not in st.session_state.data['checklist']:
            st.session_state.data['checklist'][date_key] = {}

        # 체크박스 생성 및 상태 저장
        for item in current_schedule:
            checked = st.checkbox(
                f"{item['label']} ({item['time']})",
                key=f"{date_key}_{item['id']}",
                value=st.session_state.data['checklist'][date_key].get(item['id'], False)
            )
            st.session_state.data['checklist'][date_key][item['id']] = checked

        # 학습 시간 입력
        st.subheader('학습 시간 기록')
        
        # 학습 시간 기록 초기화
        if date_key not in st.session_state.data['study_hours']:
            st.session_state.data['study_hours'][date_key] = []
        
        # 이전 형식의 데이터를 새로운 형식으로 변환
        if isinstance(st.session_state.data['study_hours'].get(date_key), (int, float)):
            st.session_state.data['study_hours'][date_key] = [{
                'hours': float(st.session_state.data['study_hours'][date_key]),
                'memo': '이전 기록',
                'timestamp': '00:00'
            }]

        # 기존 학습 기록 표시
        total_hours = 0
        if st.session_state.data['study_hours'][date_key]:
            st.write("오늘의 학습 기록:")
            for idx, record in enumerate(st.session_state.data['study_hours'][date_key]):
                total_hours += record['hours']
                st.markdown(f"- {record['hours']}시간: {record['memo']}")
            
            st.markdown(f"**총 학습 시간: {total_hours:.1f}시간**")
            st.markdown("---")

        # 새로운 학습 시간 입력
        col1, col2 = st.columns([1, 2])
        with col1:
            new_hours = st.number_input(
                '학습 시간',
                min_value=0.0,
                max_value=24.0,
                value=0.0,
                step=0.5
            )
        with col2:
            memo = st.text_input('학습 내용 (예: 수학 문제풀이, 영어 독해)', key='new_study_memo')

        if st.button('학습 시간 추가'):
            if new_hours > 0:
                st.session_state.data['study_hours'][date_key].append({
                    'hours': new_hours,
                    'memo': memo,
                    'timestamp': datetime.now().strftime('%H:%M')
                })
                st.rerun()

        # 학습 시간 초기화 버튼
        if st.button('오늘 학습 기록 초기화'):
            st.session_state.data['study_hours'][date_key] = []
            st.rerun()

        # 학습 평가
        target_hours = target_study_hours[day_type]
        if total_hours >= target_hours:
            evaluation = 'GOOD'
            color = 'green'
        elif total_hours > 0:
            evaluation = 'BAD'
            color = 'red'
        else:
            evaluation = '미입력'
            color = 'gray'

        st.markdown(f"**학습 평가:** :{color}[{evaluation}]")

        # 일일 총평
        st.subheader('오늘의 총평')
        daily_review = st.text_area(
            "오늘 하루를 돌아보며...",
            value=st.session_state.data['daily_reviews'].get(date_key, ''),
            height=150,
            placeholder="오늘의 성과, 부족한 점, 내일의 계획 등을 기록해보세요."
        )
        st.session_state.data['daily_reviews'][date_key] = daily_review

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

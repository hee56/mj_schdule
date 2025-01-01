import streamlit as st
import pandas as pd
import os
from utils.data_manager import format_time_display

def show_data_analysis():
    st.markdown("### 학습 데이터 분석")
    
    if not os.path.exists('data/activities_data.csv'):
        st.warning("아직 저장된 데이터가 없습니다.")
        return
        
    # 데이터 로드
    df = pd.read_csv('data/activities_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["일별 분석", "월별 분석", "상세 데이터"])
    
    with tab1:
        st.subheader("일별 학습/휴식 시간")
        
        # 일별 총계 계산
        daily_summary = df.pivot_table(
            index='date',
            columns='activity_type',
            values='hours',
            aggfunc='sum'
        ).reset_index().fillna(0)
        
        daily_summary = daily_summary.sort_values('date')
        
        # 차트 생성
        st.line_chart(
            daily_summary.set_index('date')[['study', 'break']],
            use_container_width=True
        )
        
        # 통계 표시
        st.markdown("#### 일별 통계")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_study = daily_summary['study'].mean()
            st.metric("평균 학습 시간", f"{avg_study:.1f}시간")
            
        with col2:
            avg_break = daily_summary['break'].mean()
            st.metric("평균 휴식 시간", f"{avg_break:.1f}시간")
            
        with col3:
            study_days = len(daily_summary[daily_summary['study'] > 0])
            st.metric("총 학습 일수", f"{study_days}일")
    
    with tab2:
        st.subheader("월별 학습/휴식 시간")
        
        # 월별 총계 계산
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_summary = df.pivot_table(
            index='month',
            columns='activity_type',
            values='hours',
            aggfunc='sum'
        ).reset_index().fillna(0)
        
        monthly_summary = monthly_summary.sort_values('month')
        
        # 차트 생성
        st.bar_chart(
            monthly_summary.set_index('month')[['study', 'break']],
            use_container_width=True
        )
        
        # 월별 상세 데이터
        st.markdown("#### 월별 상세 데이터")
        st.dataframe(monthly_summary.style.format({
            'study': '{:.1f}시간',
            'break': '{:.1f}시간'
        }))
    
    with tab3:
        st.subheader("전체 기록 데이터")
        
        # 데이터 정렬 및 포맷팅
        display_df = df.sort_values('date', ascending=False).copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df = display_df.rename(columns={
            'date': '날짜',
            'activity_type': '활동 유형',
            'hours': '시간',
            'memo': '메모',
            'timestamp': '기록 시각'
        })
        
        # 활동 유형 한글화
        display_df['활동 유형'] = display_df['활동 유형'].map({
            'study': '학습',
            'break': '휴식'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # CSV 다운로드 버튼
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name="학습기록.csv",
            mime="text/csv"
        )

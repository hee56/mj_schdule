import pandas as pd
import os
from datetime import datetime

def load_data():
    data = {
        'activities': {},
        'checklist': {},
        'reviews': {}
    }
    
    if os.path.exists('data/checklist_data.csv'):
        checklist_df = pd.read_csv('data/checklist_data.csv')
        for _, row in checklist_df.iterrows():
            date = row['date']
            if date not in data['checklist']:
                data['checklist'][date] = {}
            data['checklist'][date][row['item_id']] = row['checked']

    if os.path.exists('data/activities_data.csv'):
        activities_df = pd.read_csv('data/activities_data.csv')
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

    if os.path.exists('data/reviews_data.csv'):
        reviews_df = pd.read_csv('data/reviews_data.csv')
        for _, row in reviews_df.iterrows():
            date = row['date']
            data['reviews'][date] = {
                'content': row['content'],
                'timestamp': row['timestamp']
            }
    
    return data

def save_data(data):
    os.makedirs('data', exist_ok=True)
    
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
        checklist_df.to_csv('data/checklist_data.csv', index=False)

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
        activities_df.to_csv('data/activities_data.csv', index=False)

    review_records = []
    for date, review in data['reviews'].items():
        review_records.append({
            'date': date,
            'content': review['content'],
            'timestamp': review['timestamp']
        })
    
    if review_records:
        reviews_df = pd.DataFrame(review_records)
        reviews_df.to_csv('data/reviews_data.csv', index=False)

def backup_data():
    backup_dir = 'backup'
    os.makedirs(backup_dir, exist_ok=True)
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for filename in ['checklist_data.csv', 'activities_data.csv', 'reviews_data.csv']:
        if os.path.exists(f'data/{filename}'):
            df = pd.read_csv(f'data/{filename}')
            df.to_csv(f'{backup_dir}/{filename.split(".")[0]}_{backup_time}.csv', index=False)

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

def format_time_display(total_hours):
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    if minutes > 0:
        return f"{hours}시간 {minutes}분"
    return f"{hours}시간"

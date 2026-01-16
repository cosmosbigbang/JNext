"""
Firestore chat_history 확인 스크립트
최근 대화 내역 조회
"""
import os
import django
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.db_service import FirestoreService

def check_chat_history():
    db = FirestoreService.get_client()
    
    print("=" * 60)
    print("📋 Chat History 확인")
    print("=" * 60)
    
    # chat_history 컬렉션 조회
    chats = db.collection('chat_history').order_by('timestamp', direction='DESCENDING').limit(10).stream()
    
    chat_list = []
    for chat in chats:
        data = chat.to_dict()
        chat_list.append({
            'id': chat.id,
            'timestamp': data.get('timestamp'),
            'user_message': data.get('user_message', '')[:50],
            'ai_response': data.get('ai_response', '')[:50],
        })
    
    if not chat_list:
        print("❌ chat_history 컬렉션이 비어있습니다!")
        return
    
    print(f"\n📊 최근 대화 10개:")
    print("-" * 60)
    
    for i, chat in enumerate(chat_list, 1):
        timestamp = chat['timestamp']
        if timestamp:
            # Firestore timestamp를 datetime으로 변환
            if hasattr(timestamp, 'seconds'):
                dt = datetime.fromtimestamp(timestamp.seconds)
            else:
                dt = timestamp
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = 'N/A'
        
        print(f"\n{i}. ID: {chat['id']}")
        print(f"   시간: {time_str}")
        print(f"   사용자: {chat['user_message']}...")
        print(f"   AI: {chat['ai_response']}...")
    
    # 오늘 날짜 대화 확인
    today = datetime.now().date()
    print(f"\n" + "=" * 60)
    print(f"📅 오늘({today}) 대화 확인:")
    print("=" * 60)
    
    today_chats = [
        chat for chat in chat_list 
        if chat['timestamp'] and 
        datetime.fromtimestamp(chat['timestamp'].seconds if hasattr(chat['timestamp'], 'seconds') else chat['timestamp'].timestamp()).date() == today
    ]
    
    if today_chats:
        print(f"✅ 오늘 대화 {len(today_chats)}개 발견!")
        for chat in today_chats:
            timestamp = chat['timestamp']
            dt = datetime.fromtimestamp(timestamp.seconds if hasattr(timestamp, 'seconds') else timestamp.timestamp())
            print(f"  - {dt.strftime('%H:%M:%S')}: {chat['user_message']}...")
    else:
        print(f"❌ 오늘 대화가 없습니다!")
        print(f"\n가장 최근 대화:")
        if chat_list:
            latest = chat_list[0]
            timestamp = latest['timestamp']
            if timestamp:
                dt = datetime.fromtimestamp(timestamp.seconds if hasattr(timestamp, 'seconds') else timestamp.timestamp())
                print(f"  날짜: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  내용: {latest['user_message']}...")

if __name__ == '__main__':
    check_chat_history()

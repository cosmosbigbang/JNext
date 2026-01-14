"""
JNext v2 종합 테스트 스크립트
- 듀얼 슬라이더 (Temperature + DB Focus)
- 3-stage storage (chat_history → RAW)
- Hierarchical Firestore 쿼리
- AI 자기언급 제거

실행: python test_v2_complete.py
"""

import os
import sys
import json
import requests
from datetime import datetime

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from firebase_admin import firestore
from api.projects.project_manager import ProjectManager

BASE_URL = "http://localhost:8000"


def test_1_dual_sliders():
    """테스트 1: 듀얼 슬라이더 파라미터 전송"""
    print("\n" + "="*60)
    print("테스트 1: 듀얼 슬라이더 (Temperature + DB Focus)")
    print("="*60)
    
    test_cases = [
        {"temperature": 85, "db_focus": 25, "expected": "대화 모드 (창의적, DB 25%)"},
        {"temperature": 85, "db_focus": 50, "expected": "프로젝트 모드 (창의적, DB 50%)"},
        {"temperature": 40, "db_focus": 50, "expected": "프로젝트 모드 (논리적, DB 50%)"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}: {case['expected']}")
        print(f"  - Temperature: {case['temperature']} (→ {case['temperature']/100:.2f})")
        print(f"  - DB Focus: {case['db_focus']}%")
        
        payload = {
            "message": f"테스트 메시지 {i}: 슬라이더 파라미터 확인",
            "temperature": case['temperature'],
            "db_focus": case['db_focus'],
            "model": "gemini-flash"  # Gemini로 테스트
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v2/chat/", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 성공: {data.get('message', 'N/A')[:100]}")
            else:
                print(f"  ❌ 실패: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ 에러: {e}")


def test_2_raw_storage():
    """테스트 2: 3-stage storage (RAW 저장)"""
    print("\n" + "="*60)
    print("테스트 2: 3-Stage Storage (프로젝트 RAW 저장)")
    print("="*60)
    
    db = firestore.client()
    
    # 저장 전 RAW 문서 개수
    before_count = len(list(db.collection('projects').document('hinobalance').collection('raw').stream()))
    print(f"\n저장 전 RAW 문서 개수: {before_count}")
    
    # 프로젝트 모드로 메시지 전송 (GPT 사용)
    payload = {
        "message": "하이노워킹 전진 동작의 핵심 포인트는 무엇인가요?",
        "temperature": 85,
        "db_focus": 50,
        "project": "hinobalance",
        "model": "gpt"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v2/chat/", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 채팅 응답 성공")
            print(f"응답: {data.get('message', 'N/A')[:200]}...")
            
            # 5초 대기 (AI 평가 및 분석 시간)
            import time
            print("\n⏳ RAW 저장 프로세스 대기 중 (5초)...")
            time.sleep(5)
            
            # 저장 후 RAW 문서 개수
            after_count = len(list(db.collection('projects').document('hinobalance').collection('raw').stream()))
            print(f"\n저장 후 RAW 문서 개수: {after_count}")
            
            if after_count > before_count:
                print(f"✅ RAW 저장 성공! (+{after_count - before_count}개 문서)")
                
                # 최신 문서 확인
                latest_doc = db.collection('projects').document('hinobalance').collection('raw').order_by('시간', direction=firestore.Query.DESCENDING).limit(1).stream()
                for doc in latest_doc:
                    data = doc.to_dict()
                    print(f"\n최신 RAW 문서:")
                    print(f"  - ID: {doc.id}")
                    print(f"  - 제목: {data.get('제목', 'N/A')}")
                    print(f"  - 카테고리: {data.get('카테고리', 'N/A')}")
                    print(f"  - 키워드: {data.get('키워드', [])}")
                    print(f"  - 요약: {data.get('요약', 'N/A')[:100]}")
            else:
                print("⚠️ RAW 저장 실패 또는 평가 단계에서 필터링됨")
        else:
            print(f"❌ 채팅 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 에러: {e}")


def test_3_hierarchical_queries():
    """테스트 3: Hierarchical Firestore 쿼리"""
    print("\n" + "="*60)
    print("테스트 3: Hierarchical Firestore 쿼리")
    print("="*60)
    
    db = firestore.client()
    
    subcollections = ['raw', 'draft', 'final']
    
    for subcol in subcollections:
        try:
            docs = list(db.collection('projects').document('hinobalance').collection(subcol).limit(5).stream())
            print(f"\n✅ projects/hinobalance/{subcol}: {len(docs)}개 문서")
            
            if docs:
                for doc in docs[:2]:  # 처음 2개만
                    data = doc.to_dict()
                    title = data.get('제목') or data.get('title') or 'N/A'
                    category = data.get('카테고리') or data.get('category') or 'N/A'
                    print(f"  - {doc.id[:20]}... | {category} | {title[:30]}")
        except Exception as e:
            print(f"❌ projects/hinobalance/{subcol}: {e}")


def test_4_ai_self_reference_removal():
    """테스트 4: AI 자기언급 제거 확인"""
    print("\n" + "="*60)
    print("테스트 4: AI 자기언급 제거 검증")
    print("="*60)
    
    db = firestore.client()
    
    # 최근 RAW 문서 3개 확인 (order_by 대신 limit 사용)
    recent_docs = db.collection('projects').document('hinobalance').collection('raw').limit(3).stream()
    
    forbidden_words = ['제가', '저는', '저희', '젠', '진', '클로', 'AI', '어시스턴트', 'assistant']
    
    for doc in recent_docs:
        data = doc.to_dict()
        title = data.get('제목', '')
        summary = data.get('요약', '')
        organized = data.get('정리본', '')
        
        found_refs = []
        for word in forbidden_words:
            if word in title or word in summary or word in organized:
                found_refs.append(word)
        
        if found_refs:
            print(f"\n⚠️ {doc.id[:20]}... - AI 자기언급 발견: {found_refs}")
            print(f"  제목: {title}")
            print(f"  요약: {summary[:100]}")
        else:
            print(f"\n✅ {doc.id[:20]}... - AI 자기언급 없음")


def test_5_project_manager():
    """테스트 5: ProjectManager 프로젝트 로딩"""
    print("\n" + "="*60)
    print("테스트 5: ProjectManager 프로젝트 로딩")
    print("="*60)
    
    try:
        from api.projects.project_manager import ProjectManager
        manager = ProjectManager()
        project = manager.get_project('hinobalance')
        print(f"\n✅ 프로젝트 로딩 성공: {project.project_id}")
        
        # get_db_context 테스트
        context = project.get_db_context(limit=5)
        print(f"\n✅ DB 컨텍스트 조회 성공 ({len(context)} bytes)")
        print(f"컨텍스트 미리보기:\n{context[:300]}...")
        
    except Exception as e:
        print(f"❌ 에러: {e}")


def test_6_chat_history_schema():
    """테스트 6: chat_history 확장 스키마 확인"""
    print("\n" + "="*60)
    print("테스트 6: chat_history 확장 스키마")
    print("="*60)
    
    db = firestore.client()
    
    # 최근 chat_history 문서 확인 (order_by 대신 limit 사용)
    recent_chats = db.collection('chat_history').limit(3).stream()
    
    required_fields = ['temperature', 'db_focus', 'project_context', 'raw_분석_완료', 'raw_저장_위치']
    
    for doc in recent_chats:
        data = doc.to_dict()
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"\n⚠️ {doc.id[:20]}... - 누락 필드: {missing_fields}")
        else:
            print(f"\n✅ {doc.id[:20]}... - 모든 필드 존재")
            print(f"  - Temperature: {data.get('temperature')}")
            print(f"  - DB Focus: {data.get('db_focus')}%")
            print(f"  - Project: {data.get('project_context', 'N/A')}")
            print(f"  - RAW 분석: {data.get('raw_분석_완료', False)}")


def main():
    """전체 테스트 실행"""
    print("\n" + "="*80)
    print("JNext v2 종합 테스트 시작")
    print("="*80)
    
    tests = [
        ("듀얼 슬라이더", test_1_dual_sliders),
        ("3-Stage Storage", test_2_raw_storage),
        ("Hierarchical 쿼리", test_3_hierarchical_queries),
        ("AI 자기언급 제거", test_4_ai_self_reference_removal),
        ("ProjectManager", test_5_project_manager),
        ("chat_history 스키마", test_6_chat_history_schema),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n\n❌ 테스트 중단됨")
            break
        except Exception as e:
            print(f"\n❌ {name} 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("JNext v2 종합 테스트 완료")
    print("="*80)


if __name__ == "__main__":
    main()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from datetime import datetime


@csrf_exempt
def firebase_test(request):
    """
    [GET] Firestore 연결 테스트
    system_logs 컬렉션에 시스템 초기화 로그 추가
    """
    try:
        db = firestore.client()
        
        # 현재 시간
        current_time = datetime.now().isoformat()
        
        # system_logs 컬렉션에 데이터 추가
        test_data = {
            'status': 'JNext System Initialized',
            'timestamp': current_time,
            'source': 'JNext Backend API',
            'message': 'Firebase Firestore 연결 테스트 성공'
        }
        
        # Firestore에 데이터 추가
        doc_ref = db.collection('system_logs').add(test_data)
        doc_id = doc_ref[1].id
        
        # 성공 응답
        return JsonResponse({
            'status': 'success',
            'message': 'Firebase 연결 성공! system_logs에 데이터가 추가되었습니다.',
            'document_id': doc_id,
            'data': test_data,
            'firestore_url': 'https://console.firebase.google.com/project/_/firestore'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Firebase 연결 실패: {str(e)}',
            'help': [
                '1. Firebase Console에서 서비스 계정 키 다운로드',
                '2. jnext-service-account.json 파일을 JNext 루트 또는 backend 폴더에 저장',
                '3. .env 파일에서 FIREBASE_CREDENTIALS_PATH 확인'
            ]
        }, status=500)


@csrf_exempt
def system_logs_list(request):
    """
    [GET] system_logs 컬렉션의 모든 로그 조회
    """
    try:
        db = firestore.client()
        
        # system_logs 컬렉션의 모든 문서 가져오기
        docs = db.collection('system_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
        
        logs = []
        for doc in docs:
            log_data = doc.to_dict()
            log_data['id'] = doc.id
            logs.append(log_data)
        
        return JsonResponse({
            'status': 'success',
            'count': len(logs),
            'logs': logs
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'로그 조회 실패: {str(e)}'
        }, status=500)


def index(request):
    """
    [GET] API 인덱스 페이지
    """
    return JsonResponse({
        'message': 'JNext Backend API',
        'version': '1.0.0',
        'endpoints': {
            '/api/test/': 'Firebase 연결 테스트 (GET)',
            '/api/logs/': 'System logs 조회 (GET)',
            '/admin/': 'Django Admin Panel'
        }
    })

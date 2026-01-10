from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
from django.conf import settings
import json
from .ai_service import call_ai_model, classify_intent, validate_ai_response  # Phase 6: 의도 분류, 검증 추가
from .db_service import FirestoreService  # DB 서비스 레이어
from .meme_generator import MemeGenerator  # 밈 생성기

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def now_kst():
    """한국 시간 반환"""
    return datetime.now(KST)

# Phase 6: 세션 저장소 (간이 구현, 실제로는 Django 세션 사용 권장)
last_ai_response = None
last_user_message = None


def determine_save_targets(user_message, checkbox_values):
    """
    저장 위치 결정 (우선순위: 명령어 > 체크박스 > AI 추천)
    
    Args:
        user_message: J님의 메시지
        checkbox_values: UI 체크박스 선택값 ['raw', 'draft', 'final']
    
    Returns:
        list: 실제 저장할 컬렉션 리스트
    """
    # 1순위: 명령어 파싱
    if user_message.startswith('/'):
        command = user_message.split()[0].lower()
        if command == '/raw':
            return ['raw']
        elif command == '/draft':
            return ['draft']
        elif command == '/final':
            return ['final']
        elif command == '/all':
            return ['raw', 'draft', 'final']
    
    # 2순위: 체크박스 값
    if checkbox_values:
        return checkbox_values
    
    # 3순위: AI 자동 판단
    if '초안' in user_message or '아이디어' in user_message:
        return ['raw']
    elif '정리' in user_message or '통합' in user_message:
        return ['draft']
    elif '최종' in user_message or '완성' in user_message:
        return ['final']
    
    # 기본값: draft
    return ['draft']


def search_firestore(collections=None, limit=50):
    """
    Firestore 데이터 조회 함수 (하위 호환성 유지)
    새 코드는 FirestoreService.query_collections() 사용 권장
    
    Args:
        collections: 조회할 컬렉션 리스트 (None이면 3단계 컬렉션 모두)
        limit: 각 컬렉션당 최대 문서 수
    
    Returns:
        dict: {collection_name: [documents]}
    """
    return FirestoreService.query_collections(collections, limit=limit)


def chat_ui(request):
    """
    [GET] 채팅 인터페이스 (웹 UI)
    Phase 5: 웹 UI
    """
    from django.shortcuts import render
    return render(request, 'chat.html')


@csrf_exempt
def firebase_test(request):
    """
    [GET] Firestore 연결 테스트
    system_logs 컬렉션에 시스템 초기화 로그 추가
    """
    try:
        db = firestore.client()
        
        # 현재 시간 (한국 시간)
        current_time = now_kst().isoformat()
        
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
        'version': '2.2.0',
        'endpoints': {
            '/api/test/': 'Firebase 연결 테스트 (GET)',
            '/api/logs/': 'System logs 조회 (GET)',
            '/api/v1/execute-command/': '명령어 실행 API (POST) - Phase 2',
            '/api/v1/execute/': '통합 Execute API (POST) - Phase 2-2 Gen용',
            '/admin/': 'Django Admin Panel'
        }
    })


# ==================== Phase 2: 명령어 파싱 엔진 ====================

def verify_api_key(request):
    """
    API Key 검증 헬퍼 함수
    """
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
    
    # API Key가 설정되어 있고, 요청 키와 일치하는지 확인
    if hasattr(settings, 'JNEXT_API_KEY') and settings.JNEXT_API_KEY:
        if api_key != settings.JNEXT_API_KEY:
            return False
    # API Key가 설정되지 않은 경우 (개발 환경) - 모든 요청 허용
    return True


@csrf_exempt
def execute_command(request):
    """
    [POST] 대화형 DB 관리 엔진
    
    JSON 요청 형식:
    {
        "command": "CREATE_OR_UPDATE" | "READ" | "DELETE",
        "collection": "컬렉션명",
        "payload": {
            "document_id": "문서ID (선택, UPDATE/DELETE 시)",
            "data": { ... } (CREATE/UPDATE 시),
            "filters": { ... } (READ 시, 선택)
        }
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    # API Key 검증
    if not verify_api_key(request):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid API Key'
        }, status=401)
    
    try:
        # JSON 파싱
        body = json.loads(request.body)
        command = body.get('command', '').upper()
        collection = body.get('collection')
        payload = body.get('payload', {})
        
        # 필수 필드 검증
        if not command or not collection:
            return JsonResponse({
                'status': 'error',
                'message': 'command와 collection은 필수입니다.',
                'example': {
                    'command': 'CREATE_OR_UPDATE',
                    'collection': 'users',
                    'payload': {'data': {'name': 'John'}}
                }
            }, status=400)
        
        # Firestore 클라이언트
        db = firestore.client()
        
        # 명령어 분기 처리
        if command == 'CREATE_OR_UPDATE':
            return handle_create_or_update(db, collection, payload)
        elif command == 'READ':
            return handle_read(db, collection, payload)
        elif command == 'DELETE':
            return handle_delete(db, collection, payload)
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'알 수 없는 명령어: {command}',
                'allowed_commands': ['CREATE_OR_UPDATE', 'READ', 'DELETE']
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'서버 오류: {str(e)}'
        }, status=500)


def handle_create_or_update(db, collection, payload):
    """
    CREATE_OR_UPDATE 명령어 처리
    """
    document_id = payload.get('document_id')
    data = payload.get('data', {})
    
    if not data:
        return JsonResponse({
            'status': 'error',
            'message': 'payload.data가 필요합니다.'
        }, status=400)
    
    # 타임스탬프 자동 추가
    data['updated_at'] = firestore.SERVER_TIMESTAMP
    
    try:
        if document_id:
            # UPDATE: 특정 문서 업데이트
            doc_ref = db.collection(collection).document(document_id)
            doc_ref.set(data, merge=True)
            return JsonResponse({
                'status': 'success',
                'command': 'UPDATE',
                'collection': collection,
                'document_id': document_id,
                'message': f'{collection}/{document_id} 문서가 업데이트되었습니다.'
            })
        else:
            # CREATE: 새 문서 생성
            data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref = db.collection(collection).add(data)
            new_doc_id = doc_ref[1].id
            return JsonResponse({
                'status': 'success',
                'command': 'CREATE',
                'collection': collection,
                'document_id': new_doc_id,
                'message': f'{collection}에 새 문서가 생성되었습니다.'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'CREATE_OR_UPDATE 실패: {str(e)}'
        }, status=500)


def handle_read(db, collection, payload):
    """
    READ 명령어 처리
    """
    document_id = payload.get('document_id')
    filters = payload.get('filters', {})
    limit = payload.get('limit', 100)
    
    try:
        if document_id:
            # 특정 문서 조회
            doc = db.collection(collection).document(document_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return JsonResponse({
                    'status': 'success',
                    'command': 'READ',
                    'collection': collection,
                    'document': data
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{collection}/{document_id} 문서를 찾을 수 없습니다.'
                }, status=404)
        else:
            # 컬렉션 전체 조회 (필터 적용 가능)
            query = db.collection(collection)
            
            # 간단한 필터 적용 (예: {"status": "active"})
            for field, value in filters.items():
                query = query.where(field, '==', value)
            
            docs = query.limit(limit).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return JsonResponse({
                'status': 'success',
                'command': 'READ',
                'collection': collection,
                'count': len(results),
                'documents': results
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'READ 실패: {str(e)}'
        }, status=500)


def handle_delete(db, collection, payload):
    """
    DELETE 명령어 처리
    """
    document_id = payload.get('document_id')
    
    if not document_id:
        return JsonResponse({
            'status': 'error',
            'message': 'DELETE 명령어는 payload.document_id가 필요합니다.'
        }, status=400)
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        
        # 문서 존재 확인
        if not doc_ref.get().exists:
            return JsonResponse({
                'status': 'error',
                'message': f'{collection}/{document_id} 문서를 찾을 수 없습니다.'
            }, status=404)
        
        # 삭제
        doc_ref.delete()
        
        return JsonResponse({
            'status': 'success',
            'command': 'DELETE',
            'collection': collection,
            'document_id': document_id,
            'message': f'{collection}/{document_id} 문서가 삭제되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'DELETE 실패: {str(e)}'
        }, status=500)


# ==================== Phase 2-2: 통합 Execute API ====================

@csrf_exempt
def execute(request):
    """
    [POST] 통합 명령 실행 API (Gen 대화창용)
    
    JSON 요청 형식:
    {
        "action": "CREATE" | "READ" | "UPDATE" | "DELETE",
        "collection": "컬렉션명",
        "payload": { "key": "value", ... },
        "document_id": "문서ID (UPDATE/DELETE 시 필수)"
    }
    
    응답 형식:
    {
        "status": "success" | "error",
        "action": "실행된 액션",
        "collection": "컬렉션명",
        "document_id": "문서ID (있는 경우)",
        "message": "상세 메시지",
        "data": { ... } (READ 시)
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    # API Key 검증
    if not verify_api_key(request):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid API Key'
        }, status=401)
    
    try:
        # JSON 파싱
        body = json.loads(request.body)
        action = body.get('action', '').upper()
        collection = body.get('collection')
        payload = body.get('payload', {})
        document_id = body.get('document_id')
        
        # 필수 필드 검증
        if not action or not collection:
            return JsonResponse({
                'status': 'error',
                'message': 'action과 collection은 필수입니다.',
                'example': {
                    'action': 'CREATE',
                    'collection': 'users',
                    'payload': {'name': 'John', 'age': 25}
                }
            }, status=400)
        
        # Firestore 클라이언트
        db = firestore.client()
        
        # Action 분기 처리
        if action == 'CREATE':
            return handle_create_action(db, collection, payload)
        elif action == 'READ':
            return handle_read_action(db, collection, payload, document_id)
        elif action == 'UPDATE':
            return handle_update_action(db, collection, payload, document_id)
        elif action == 'DELETE':
            return handle_delete_action(db, collection, document_id)
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'알 수 없는 액션: {action}',
                'allowed_actions': ['CREATE', 'READ', 'UPDATE', 'DELETE']
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'서버 오류: {str(e)}'
        }, status=500)


def handle_create_action(db, collection, payload):
    """CREATE 액션 처리"""
    if not payload:
        return JsonResponse({
            'status': 'error',
            'message': 'payload가 필요합니다.'
        }, status=400)
    
    try:
        # 타임스탬프 자동 추가
        payload['created_at'] = firestore.SERVER_TIMESTAMP
        payload['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # 새 문서 생성
        doc_ref = db.collection(collection).add(payload)
        doc_id = doc_ref[1].id
        
        return JsonResponse({
            'status': 'success',
            'action': 'CREATE',
            'collection': collection,
            'document_id': doc_id,
            'message': f'{collection} 컬렉션에 새 문서가 생성되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'CREATE 실패: {str(e)}'
        }, status=500)


def handle_read_action(db, collection, payload, document_id=None):
    """READ 액션 처리"""
    try:
        if document_id:
            # 특정 문서 조회
            doc = db.collection(collection).document(document_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return JsonResponse({
                    'status': 'success',
                    'action': 'READ',
                    'collection': collection,
                    'document_id': doc.id,
                    'data': data,
                    'message': '문서 조회 성공'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{collection}/{document_id} 문서를 찾을 수 없습니다.'
                }, status=404)
        else:
            # 컬렉션 전체 조회 (필터 적용 가능)
            query = db.collection(collection)
            
            # payload에서 필터 추출
            filters = payload.get('filters', {})
            for field, value in filters.items():
                query = query.where(field, '==', value)
            
            # limit 설정
            limit = payload.get('limit', 100)
            docs = query.limit(limit).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return JsonResponse({
                'status': 'success',
                'action': 'READ',
                'collection': collection,
                'count': len(results),
                'data': results,
                'message': f'{len(results)}개의 문서를 조회했습니다.'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'READ 실패: {str(e)}'
        }, status=500)


def handle_update_action(db, collection, payload, document_id):
    """UPDATE 액션 처리"""
    if not document_id:
        return JsonResponse({
            'status': 'error',
            'message': 'UPDATE 액션은 document_id가 필요합니다.'
        }, status=400)
    
    if not payload:
        return JsonResponse({
            'status': 'error',
            'message': 'payload가 필요합니다.'
        }, status=400)
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        
        # 문서 존재 확인
        if not doc_ref.get().exists:
            return JsonResponse({
                'status': 'error',
                'message': f'{collection}/{document_id} 문서를 찾을 수 없습니다.'
            }, status=404)
        
        # 타임스탬프 업데이트
        payload['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # 문서 업데이트
        doc_ref.update(payload)
        
        return JsonResponse({
            'status': 'success',
            'action': 'UPDATE',
            'collection': collection,
            'document_id': document_id,
            'message': f'{collection}/{document_id} 문서가 업데이트되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'UPDATE 실패: {str(e)}'
        }, status=500)


def handle_delete_action(db, collection, document_id):
    """DELETE 액션 처리"""
    if not document_id:
        return JsonResponse({
            'status': 'error',
            'message': 'DELETE 액션은 document_id가 필요합니다.'
        }, status=400)
    
    try:
        doc_ref = db.collection(collection).document(document_id)
        
        # 문서 존재 확인
        if not doc_ref.get().exists:
            return JsonResponse({
                'status': 'error',
                'message': f'{collection}/{document_id} 문서를 찾을 수 없습니다.'
            }, status=404)
        
        # 삭제
        doc_ref.delete()
        
        return JsonResponse({
            'status': 'success',
            'action': 'DELETE',
            'collection': collection,
            'document_id': document_id,
            'message': f'{collection}/{document_id} 문서가 삭제되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'DELETE 실패: {str(e)}'
        }, status=500)


@csrf_exempt
def chat(request):
    """
    [GET/POST] Gemini AI 채팅 API
    Phase 3: Gemini AI 통합
    
    Body:
    {
        "message": "J님의 메시지",
        "mode": "organize" | "analysis"
    }
    """
    # GET 요청: API 정보 반환
    if request.method == 'GET':
        return JsonResponse({
            'status': 'info',
            'endpoint': '/api/v1/chat/',
            'method': 'POST',
            'gemini_initialized': settings.GEMINI_INITIALIZED,
            'gemini_model': settings.GEMINI_MODEL if settings.GEMINI_INITIALIZED else None,
            'body': {
                'message': 'J님의 메시지 (필수)',
                'mode': 'organize 또는 analysis (기본값: organize)'
            },
            'example_curl': 'curl -X POST http://127.0.0.1:8000/api/v1/chat/ -H "Content-Type: application/json" -d "{\\"message\\": \\"안녕하세요\\", \\"mode\\": \\"organize\\"}"'
        })
    
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 메서드만 지원합니다.'
        }, status=405)
    
    # Gemini 초기화 확인
    if not settings.GEMINI_INITIALIZED:
        return JsonResponse({
            'status': 'error',
            'message': 'Gemini AI가 초기화되지 않았습니다. GEMINI_API_KEY를 확인하세요.'
        }, status=500)
    
    try:
        # 요청 데이터 파싱
        data = json.loads(request.body)
        user_message = data.get('message', '')
        mode = data.get('mode', 'hybrid')  # organize | hybrid | analysis (기본값: hybrid)
        model = data.get('model', settings.DEFAULT_AI_MODEL)  # gemini | gpt | claude | all
        checkbox_save_targets = data.get('save_targets', [])  # UI 체크박스 값
        
        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'message 필드가 필요합니다.'
            }, status=400)
        
        # 저장 위치 결정 (우선순위 적용)
        save_targets = determine_save_targets(user_message, checkbox_save_targets)
        
        # Phase 6: 의도 분류
        global last_ai_response, last_user_message
        intent_data = classify_intent(user_message)
        intent = intent_data['intent']
        
        # SAVE 의도 처리
        if intent == 'SAVE':
            if not last_ai_response:
                return JsonResponse({
                    'status': 'error',
                    'message': '저장할 답변이 없습니다. 먼저 질문을 해주세요.'
                }, status=400)
            
            # 자동 저장
            collection = intent_data['params']['collection']
            title = f"{last_user_message[:30]}... 정리" if last_user_message else "AI 답변 정리"
            
            # Gemini에게 출판용 전체 글 생성 요청
            publish_prompt = f"""
다음 내용을 블로그나 책에 바로 출판할 수 있는 완성된 글로 작성해주세요.

**요구사항:**
- 전문적이고 읽기 쉬운 문체
- 명확한 구조 (Introduction, 본문, Conclusion)
- 마크다운 형식 (##, ###, -, > 등 사용)
- 길이: 1000-2000자

**원본 질문:** {last_user_message}

**AI 분석 결과:**
{last_ai_response.get('answer', '')}

**핵심 주장:**
""" + '\n'.join(f"- {claim}" for claim in last_ai_response.get('claims', [])[:5]) + """

위 내용을 기반으로 출판 가능한 전체 글을 작성해주세요.
"""
            
            # Gemini 호출로 출판용 글 생성
            try:
                import google.genai as genai
                client = settings.AI_MODELS['gemini']['client']
                model = settings.AI_MODELS['gemini']['model']
                
                publish_response = client.models.generate_content(
                    model=model,
                    contents=publish_prompt,
                    config={'temperature': 0.8}  # 창의적 글쓰기
                )
                
                full_article = publish_response.text
            except Exception as e:
                print(f"[출판용 글 생성 실패] {str(e)}")
                # 실패 시 기본 포맷으로 대체
                full_article = f"# {title}\n\n{last_ai_response.get('answer', '')}\n\n## 핵심 주장\n" + '\n'.join(f"- {claim}" for claim in last_ai_response.get('claims', []))
            
            # formatResponseForSave 로직을 Python으로 구현 (요약용)
            content = f"# {last_ai_response.get('answer', '')}\n\n"
            
            if last_ai_response.get('claims'):
                content += "## 핵심 주장\n"
                for idx, claim in enumerate(last_ai_response['claims'], 1):
                    content += f"{idx}. {claim}\n"
                content += '\n'
            
            if last_ai_response.get('evidence'):
                content += "## 근거\n"
                for idx, ev in enumerate(last_ai_response['evidence'], 1):
                    content += f"[{idx}] {ev.get('collection', '')}/{ev.get('doc_id', '')}\n"
                    content += f"   {ev.get('field', '')}: {ev.get('value', '')}\n\n"
            
            # Firestore에 저장
            db = firestore.client()
            doc_data = {
                '제목': title,
                '카테고리': '기타',
                '운동명': '',  # 중분류 (운동명)
                '내용': content,  # 요약본
                '전체글': full_article,  # 출판용 전체 글
                '원본질문': last_user_message,
                'AI응답': last_ai_response,
                '데이터상태': 'FINAL' if collection == 'hino_final' else 'DRAFT',
                '작성일시': now_kst(),
                '작성자': 'J님 (자동저장)',
                '종류': '정리'
            }
            
            doc_ref = db.collection(collection).add(doc_data)
            doc_id = doc_ref[1].id
            
            return JsonResponse({
                'status': 'success',
                'action': 'SAVE',
                'message': f'✅ {collection}에 자동 저장되었습니다!',
                'doc_id': doc_id,
                'collection': collection,
                'response': {
                    'answer': f'"{last_user_message[:50]}..." 답변을 {collection}에 저장했습니다.',
                    'claims': [f'문서 ID: {doc_id}', f'컬렉션: {collection}'],
                    'evidence': [],
                    'missing_info': [],
                    'confidence': 1.0
                }
            })
        
        # READ 의도 처리
        if intent == 'READ':
            params = intent_data['params']
            collections = params['collections'] if params['collections'] else None
            category_filter = params.get('category')
            
            # 필터링된 데이터 조회
            db_data = search_firestore(collections=collections)
            
            # 카테고리 필터링 및 문서 리스트 생성
            document_list = []
            if category_filter:
                for col_name, documents in db_data.items():
                    if isinstance(documents, list):
                        filtered = [
                            doc for doc in documents 
                            if doc.get('카테고리') == category_filter
                        ]
                        db_data[col_name] = filtered
                        
                        # 문서 리스트에 추가
                        for doc in filtered:
                            created_at = doc.get('작성일시') or doc.get('created_at')
                            if created_at:
                                created_at_str = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
                            else:
                                created_at_str = 'N/A'
                            
                            document_list.append({
                                'collection': col_name,
                                'doc_id': doc.get('_id'),
                                'title': doc.get('제목', doc.get('내용', '')[:30] + '...'),
                                'category': doc.get('카테고리', ''),
                                'preview': doc.get('내용', '')[:100] + '...' if len(doc.get('내용', '')) > 100 else doc.get('내용', ''),
                                'created_at': created_at_str
                            })
            else:
                # 전체 조회 시에도 문서 리스트 생성
                for col_name, documents in db_data.items():
                    if isinstance(documents, list):
                        for doc in documents:
                            created_at = doc.get('작성일시') or doc.get('created_at')
                            if created_at:
                                created_at_str = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
                            else:
                                created_at_str = 'N/A'
                            
                            document_list.append({
                                'collection': col_name,
                                'doc_id': doc.get('_id'),
                                'title': doc.get('제목', doc.get('내용', '')[:30] + '...'),
                                'category': doc.get('카테고리', ''),
                                'preview': doc.get('내용', '')[:100] + '...' if len(doc.get('내용', '')) > 100 else doc.get('내용', ''),
                                'created_at': created_at_str
                            })
            
            # 결과 포맷팅
            total_docs = len(document_list)
            
            return JsonResponse({
                'status': 'success',
                'action': 'READ',
                'message': f'✅ {total_docs}개 문서를 찾았습니다.',
                'data': db_data,
                'document_list': document_list,  # 체크박스 UI용
                'response': {
                    'answer': f'{total_docs}개 문서를 조회했습니다.',
                    'claims': [f'{k}: {len(v)}개' for k, v in db_data.items() if isinstance(v, list)],
                    'evidence': [],
                    'missing_info': [],
                    'confidence': 1.0
                }
            })
        
        # GENERATE_FINAL 의도 처리 (자연어 방식)
        if intent == 'GENERATE_FINAL':
            params = intent_data['params']
            category = params.get('category')
            exercise_name = params.get('exercise_name')
            include_kw = params.get('include_keywords', [])
            exclude_kw = params.get('exclude_keywords', [])
            mode_type = params.get('mode', 'final')  # 'final' or 'draft'
            
            # 문서 검색
            db = firestore.client()
            collections = ['hino_draft', 'hino_raw']  # draft와 raw에서 검색
            
            all_docs = []
            for col_name in collections:
                docs = db.collection(col_name).stream()
                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_data['_id'] = doc.id
                    doc_data['_collection'] = col_name
                    
                    # 필터링
                    if category and doc_data.get('카테고리') != category:
                        continue
                    if exercise_name and doc_data.get('운동명') != exercise_name:
                        continue
                    
                    # 포함 키워드 체크
                    if include_kw:
                        content = str(doc_data.get('내용', '')) + str(doc_data.get('제목', ''))
                        if not any(kw in content for kw in include_kw):
                            continue
                    
                    # 제외 키워드 체크
                    if exclude_kw:
                        content = str(doc_data.get('내용', '')) + str(doc_data.get('제목', ''))
                        if any(kw in content for kw in exclude_kw):
                            continue
                    
                    all_docs.append(doc_data)
            
            if not all_docs:
                return JsonResponse({
                    'status': 'error',
                    'message': '❌ 조건에 맞는 문서를 찾을 수 없습니다.',
                    'response': {
                        'answer': '조건에 맞는 문서가 없습니다.',
                        'claims': [],
                        'evidence': [],
                        'missing_info': ['검색 조건을 확인해주세요.'],
                        'confidence': 0.0
                    }
                })
            
            # Gemini로 종합
            combined_content = "\n\n=== 문서 구분선 ===\n\n".join([
                f"[문서 {idx+1}]\n제목: {doc.get('제목', 'N/A')}\n카테고리: {doc.get('카테고리', 'N/A')}\n운동명: {doc.get('운동명', 'N/A')}\n\n내용:\n{doc.get('내용', '')}\n\n전체글:\n{doc.get('전체글', '')}"
                for idx, doc in enumerate(all_docs)
            ])
            
            synthesis_prompt = f"""
{len(all_docs)}개 문서를 종합하여 최종본을 작성해주세요.
{f"카테고리: {category}" if category else ""}
{f"운동명: {exercise_name}" if exercise_name else ""}
{f"포함 키워드: {', '.join(include_kw)}" if include_kw else ""}
{f"제외 키워드: {', '.join(exclude_kw)}" if exclude_kw else ""}

요구사항:
1. 전문적이고 완성도 높은 글
2. 마크다운 형식
3. 2000-5000자

원본 문서:
{combined_content}

JSON 형식:
{{
  "제목": "생성된 제목",
  "전체글": "완성된 전체 내용"
}}
"""
            
            import google.genai as genai
            client = settings.AI_MODELS['gemini']['client']
            model_name = settings.AI_MODELS['gemini']['model']
            
            synthesis_response = client.models.generate_content(
                model=model_name,
                contents=synthesis_prompt,
                config={'temperature': 0.7, 'response_mime_type': 'application/json'}
            )
            
            result = json.loads(synthesis_response.text)
            generated_title = result.get('제목', f"{category or '종합'} 정리")
            generated_content = result.get('전체글', '')
            summary = generated_content[:500] + '...' if len(generated_content) > 500 else generated_content
            
            # 저장
            target_collection = 'hino_final' if mode_type == 'final' else 'hino_draft'
            final_doc_data = {
                '제목': generated_title,
                '카테고리': category or '기타',
                '운동명': exercise_name or '',
                '내용': summary,
                '전체글': generated_content,
                '원본문서수': len(all_docs),
                '데이터상태': 'FINAL' if mode_type == 'final' else 'DRAFT',
                '작성일시': now_kst(),
                '작성자': 'J님 (AI 종합)',
                '종류': '최종본' if mode_type == 'final' else '정리본'
            }
            
            final_ref = db.collection(target_collection).add(final_doc_data)
            final_doc_id = final_ref[1].id
            
            return JsonResponse({
                'status': 'success',
                'action': 'GENERATE_FINAL',
                'message': f'✅ {len(all_docs)}개 문서를 종합하여 {target_collection}에 저장했습니다!',
                'doc_id': final_doc_id,
                'collection': target_collection,
                'response': {
                    'answer': f'"{generated_title}" 제목으로 {len(all_docs)}개 문서를 종합한 최종본이 생성되었습니다.',
                    'claims': [
                        f'카테고리: {category or "N/A"}',
                        f'운동명: {exercise_name or "N/A"}',
                        f'원본 문서: {len(all_docs)}개',
                        f'저장 위치: {target_collection}'
                    ],
                    'evidence': [],
                    'missing_info': [],
                    'confidence': 1.0
                }
            })
        
        # 일반 질문 (NONE)
        # 모드에 따른 시스템 프롬프트 선택
        if mode == 'organize':
            system_prompt = settings.ORGANIZE_SYSTEM_PROMPT
        elif mode == 'hybrid':
            system_prompt = settings.HYBRID_SYSTEM_PROMPT
        elif mode == 'analysis':
            system_prompt = settings.ANALYSIS_SYSTEM_PROMPT
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'mode는 "organize", "hybrid" 또는 "analysis"만 가능합니다.'
            }, status=400)
        
        # Phase 4-2: Firestore 데이터 조회
        db_data = search_firestore()
        
        # DB 데이터를 텍스트로 변환
        db_context = "\n=== 현재 Firestore DB 데이터 ===\n"
        total_docs = 0
        
        for collection_name, documents in db_data.items():
            if isinstance(documents, list):
                doc_count = len(documents)
                total_docs += doc_count
                db_context += f"\n## {collection_name} ({doc_count}개 문서)\n"
                
                if doc_count > 0:
                    for idx, doc in enumerate(documents[:10], 1):
                        db_context += f"\n### 문서 {idx} (ID: {doc.get('_id', 'unknown')})\n"
                        db_context += f"```json\n{json.dumps(doc, ensure_ascii=False, indent=2)}\n```\n"
                else:
                    db_context += "- 데이터 없음\n"
        
        db_context += f"\n=== 총 {total_docs}개 문서 조회됨 ===\n"
        
        # Phase 4-3: 멀티 모델 AI 호출 (JSON 응답 강제)
        ai_response = call_ai_model(
            model_name=model,
            user_message=user_message,
            system_prompt=system_prompt,
            db_context=db_context
        )
        
        # Phase 6: 세션에 저장
        last_ai_response = ai_response
        last_user_message = user_message
        
        # AI가 저장 위치 자동 판단
        suggested_collections = []
        if '초안' in user_message or '아이디어' in user_message:
            suggested_collections = ['raw']
        elif '정리' in user_message or '통합' in user_message:
            suggested_collections = ['draft']
        elif '최종' in user_message or '완성' in user_message:
            suggested_collections = ['final']
        
        return JsonResponse({
            'status': 'success',
            'mode': mode,
            'model': model,
            'user_message': user_message,  # 필드명 통일
            'response': ai_response,  # JSON 구조화된 응답
            'db_documents_count': total_docs,
            'save_targets': save_targets,  # 실제 저장될 위치
            'suggested_collections': suggested_collections  # AI 제안
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Chat API Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'Gemini API 호출 실패: {str(e)}',
            'error_type': type(e).__name__,
            'traceback': error_trace
        }, status=500)


@csrf_exempt
def save_summary(request):
    """
    [POST] AI 답변 저장
    J님이 편집한 정리 내용을 hino_draft 또는 hino_final에 저장
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        
        title = data.get('title', '제목 없음')
        category = data.get('category', '기타')
        content = data.get('content', '')
        collection = data.get('collection', 'hino_draft')
        original_message = data.get('original_message', '')
        ai_response = data.get('ai_response', {})
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': '내용이 비어있습니다.'
            }, status=400)
        
        # Firestore에 저장
        db = firestore.client()
        doc_data = {
            '제목': title,
            '카테고리': category,
            '내용': content,
            '원본질문': original_message,
            'AI응답': ai_response,
            '데이터상태': 'DRAFT' if collection == 'hino_draft' else 'FINAL',
            '작성일시': now_kst(),
            '수정일시': now_kst(),
            '작성자': 'J님',
            '종류': '정리'
        }
        
        # FINAL 단계에서만 밈 이미지 생성 (비용 최적화)
        # RAW/DRAFT는 텍스트 필드만 저장
        meme_generated = False
        
        # 밈 텍스트 필드 (모든 단계에서 저장 가능)
        meme_top = data.get('밈자막상단') or ai_response.get('밈자막상단', '')
        meme_bottom = data.get('밈자막하단') or ai_response.get('밈자막하단', '')
        meme_style = data.get('밈스타일') or ai_response.get('밈스타일', '시트콤')
        meme_character = data.get('밈캐릭터', '지피')  # 기본값: 지피
        
        # 텍스트 필드는 항상 저장
        if meme_top:
            doc_data['밈자막상단'] = meme_top
        if meme_bottom:
            doc_data['밈자막하단'] = meme_bottom
        if meme_style:
            doc_data['밈스타일'] = meme_style
        if meme_character:
            doc_data['밈캐릭터'] = meme_character
        
        # FINAL 단계에서만 실제 이미지 생성
        if collection == 'hino_final' and (meme_top or meme_bottom):
            try:
                # 밈 생성 (시트콤 캐릭터 이미지 사용)
                meme_gen = MemeGenerator()
                result = meme_gen.create_meme(
                    character=meme_character,
                    top_text=meme_top,
                    bottom_text=meme_bottom,
                    style=meme_style
                )
                
                # 이미지 URL 필드 추가
                doc_data['밈이미지URL'] = result['selected_image_name']
                doc_data['밈합성이미지URL'] = f"{result['character']}_meme.png"
                doc_data['밈생성모델'] = '진 (시트콤 캐릭터 + Pillow 합성)'
                meme_generated = True
                
                print(f"[밈 생성 성공] 캐릭터: {result['character']}, 이미지: {result['selected_image_name']}")
            except Exception as e:
                print(f"[밈 생성 실패] {str(e)}")
                import traceback
                traceback.print_exc()
                # 실패해도 문서는 저장 (이미지 URL 없이)
        
        doc_ref = db.collection(collection).add(doc_data)
        doc_id = doc_ref[1].id
        
        response_message = f'{collection}에 저장되었습니다.'
        if meme_generated:
            response_message += ' (밈 이미지 생성 완료)'
        
        return JsonResponse({
            'status': 'success',
            'message': response_message,
            'doc_id': doc_id,
            'collection': collection,
            'meme_generated': meme_generated
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Save Summary Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'저장 실패: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)


@csrf_exempt
def generate_final(request):
    """
    [POST] 선택된 문서들을 종합하여 최종본 생성
    Phase 6.5: Gemini가 여러 draft를 분석해서 final 생성
    
    Body:
    {
        "documents": [
            {"collection": "hino_draft", "doc_id": "abc123"},
            {"collection": "hino_draft", "doc_id": "def456"}
        ]
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        documents = data.get('documents', [])
        
        if not documents:
            return JsonResponse({
                'status': 'error',
                'message': '최종본 생성에 포함할 문서가 없습니다.'
            }, status=400)
        
        # Firestore에서 문서들 조회
        db = firestore.client()
        source_docs = []
        categories = set()
        exercise_names = set()
        
        for doc in documents:
            collection = doc.get('collection')
            doc_id = doc.get('doc_id')
            
            if not collection or not doc_id:
                continue
            
            doc_ref = db.collection(collection).document(doc_id)
            doc_snap = doc_ref.get()
            
            if doc_snap.exists:
                doc_data = doc_snap.to_dict()
                source_docs.append(doc_data)
                
                # 카테고리와 운동명 수집
                if '카테고리' in doc_data:
                    categories.add(doc_data['카테고리'])
                if '운동명' in doc_data and doc_data['운동명']:
                    exercise_names.add(doc_data['운동명'])
        
        if not source_docs:
            return JsonResponse({
                'status': 'error',
                'message': '유효한 문서를 찾을 수 없습니다.'
            }, status=404)
        
        # Gemini에게 종합 요청
        combined_content = "\n\n=== 문서 구분선 ===\n\n".join([
            f"[문서 {idx+1}]\n제목: {doc.get('제목', 'N/A')}\n카테고리: {doc.get('카테고리', 'N/A')}\n운동명: {doc.get('운동명', 'N/A')}\n\n내용:\n{doc.get('내용', '')}\n\n전체글:\n{doc.get('전체글', '')}"
            for idx, doc in enumerate(source_docs)
        ])
        
        category_str = ', '.join(categories) if categories else '기타'
        exercise_str = ', '.join(exercise_names) if exercise_names else ''
        
        synthesis_prompt = f"""
다음은 [{category_str}] 카테고리의 {len(source_docs)}개 문서입니다.
{f"운동명: {exercise_str}" if exercise_str else ""}

이 문서들을 종합하여 **출판 가능한 완성본**을 작성해주세요.

**요구사항:**
1. 모든 문서의 핵심 내용을 포괄적으로 통합
2. 중복 제거, 논리적 구조 재구성
3. 전문적이고 완성도 높은 문체
4. 마크다운 형식 (##, ###, -, > 등 활용)
5. 길이: 2000-5000자
6. 제목도 자동 생성

**원본 문서들:**

{combined_content}

---

위 문서들을 종합한 최종본을 다음 형식으로 작성해주세요:

JSON 형식:
{{
  "제목": "생성된 제목",
  "전체글": "완성된 전체 내용 (마크다운)"
}}
"""
        
        import google.genai as genai
        client = settings.AI_MODELS['gemini']['client']
        model = settings.AI_MODELS['gemini']['model']
        
        synthesis_response = client.models.generate_content(
            model=model,
            contents=synthesis_prompt,
            config={
                'temperature': 0.7,
                'response_mime_type': 'application/json'
            }
        )
        
        result = json.loads(synthesis_response.text)
        generated_title = result.get('제목', f"{category_str} 종합 정리")
        generated_content = result.get('전체글', '')
        
        # 요약본도 생성
        summary = generated_content[:500] + '...' if len(generated_content) > 500 else generated_content
        
        # hino_final에 저장
        final_doc_data = {
            '제목': generated_title,
            '카테고리': list(categories)[0] if categories else '기타',
            '운동명': list(exercise_names)[0] if exercise_names else '',
            '내용': summary,
            '전체글': generated_content,
            '원본문서수': len(source_docs),
            '원본문서ID': [doc.get('doc_id') for doc in documents],
            '데이터상태': 'FINAL',
            '작성일시': now_kst(),
            '작성자': 'J님 (AI 종합)',
            '종류': '최종본'
        }
        
        final_ref = db.collection('hino_final').add(final_doc_data)
        final_doc_id = final_ref[1].id
        
        return JsonResponse({
            'status': 'success',
            'message': '최종본이 생성되었습니다.',
            'doc_id': final_doc_id,
            'collection': 'hino_final',
            'title': generated_title,
            'source_count': len(source_docs)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Generate Final Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'최종본 생성 실패: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)


@csrf_exempt
def get_document(request):
    """
    [GET] 개별 문서 조회
    Phase 6: 문서 편집을 위한 전체 내용 조회
    
    Query Params:
        collection: 컴렉션 이름
        doc_id: 문서 ID
    """
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'GET 요청만 허용됩니다.'
        }, status=405)
    
    try:
        collection = request.GET.get('collection')
        doc_id = request.GET.get('doc_id')
        
        if not collection or not doc_id:
            return JsonResponse({
                'status': 'error',
                'message': '컴렉션과 문서 ID가 필요합니다.'
            }, status=400)
        
        # Firestore에서 문서 조회
        db = firestore.client()
        doc_ref = db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return JsonResponse({
                'status': 'error',
                'message': '문서를 찾을 수 없습니다.'
            }, status=404)
        
        doc_data = doc.to_dict()
        doc_data['_id'] = doc.id
        doc_data['_collection'] = collection
        
        return JsonResponse({
            'status': 'success',
            'document': doc_data
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Get Document Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'조회 실패: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)


@csrf_exempt
def update_documents(request):
    """
    [POST] 여러 문서 일괄 수정
    Phase 6: 체크박스 선택 수정
    
    Body:
    {
        "documents": [
            {"collection": "hino_draft", "doc_id": "abc123"},
            {"collection": "hino_raw", "doc_id": "def456"}
        ],
        "updates": {
            "제목": "새 제목",
            "카테고리": "하이노워킹",
            "내용": "새 내용",
            "데이터상태": "FINAL"
        }
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        documents = data.get('documents', [])
        updates = data.get('updates', {})
        
        if not documents:
            return JsonResponse({
                'status': 'error',
                'message': '수정할 문서가 없습니다.'
            }, status=400)
        
        if not updates:
            return JsonResponse({
                'status': 'error',
                'message': '수정할 내용이 없습니다.'
            }, status=400)
        
        # 수정일시 자동 추가
        updates['수정일시'] = now_kst()
        
        # Firestore에서 수정
        db = firestore.client()
        updated_count = 0
        errors = []
        
        for doc in documents:
            collection = doc.get('collection')
            doc_id = doc.get('doc_id')
            
            if not collection or not doc_id:
                errors.append(f"잘못된 문서 정보: {doc}")
                continue
            
            try:
                db.collection(collection).document(doc_id).update(updates)
                updated_count += 1
            except Exception as e:
                errors.append(f"{collection}/{doc_id}: {str(e)}")
        
        return JsonResponse({
            'status': 'success' if updated_count > 0 else 'error',
            'message': f'{updated_count}개 문서가 수정되었습니다.',
            'updated_count': updated_count,
            'errors': errors if errors else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Update Documents Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'수정 실패: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)


@csrf_exempt
def delete_documents(request):
    """
    [POST] 여러 문서 일괄 삭제
    Phase 6: 체크박스 선택 삭제
    
    Body:
    {
        "documents": [
            {"collection": "hino_draft", "doc_id": "abc123"},
            {"collection": "hino_raw", "doc_id": "def456"}
        ]
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST 요청만 허용됩니다.'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        documents = data.get('documents', [])
        
        if not documents:
            return JsonResponse({
                'status': 'error',
                'message': '삭제할 문서가 없습니다.'
            }, status=400)
        
        # Firestore에서 삭제
        db = firestore.client()
        deleted_count = 0
        errors = []
        
        for doc in documents:
            collection = doc.get('collection')
            doc_id = doc.get('doc_id')
            
            if not collection or not doc_id:
                errors.append(f"잘못된 문서 정보: {doc}")
                continue
            
            try:
                db.collection(collection).document(doc_id).delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"{collection}/{doc_id}: {str(e)}")
        
        return JsonResponse({
            'status': 'success' if deleted_count > 0 else 'error',
            'message': f'{deleted_count}개 문서가 삭제되었습니다.',
            'deleted_count': deleted_count,
            'errors': errors if errors else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Delete Documents Error] {error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': f'삭제 실패: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)

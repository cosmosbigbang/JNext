"""
JNext v2 Views
동적 맥락 시스템 기반 채팅 API
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
import json
import re

from .core.context_manager import ContextManager
from .projects.project_manager import project_manager
from .ai_service import call_ai_model
from .views import save_chat_history, load_chat_history, now_kst

# 한국 시간대
KST = timezone(timedelta(hours=9))


def remove_markdown_formatting(text):
    """
    마크다운 문법 제거 (볼드, 헤더 등)
    숫자 목록 (1. 2. 3.)은 유지
    """
    if not text:
        return text
    
    # **볼드** 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # ## 헤더 제거 (줄 시작 기준)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # ` 코드 ` 제거
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # > 인용 제거
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # - 또는 * 리스트 → 숫자 목록으로 변환하지 않고 그냥 제거
    text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)
    
    return text


@csrf_exempt
def chat_v2(request):
    """
    JNext v2 채팅 API
    동적 맥락 관리 + 슬라이더 2개 (Temperature + DB 사용률)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        # 요청 파싱
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        model = data.get('model', 'gemini-pro')  # 기본 Pro 유지 (품질 우선)
        project_id = data.get('project', None)  # None = 일반 대화
        temperature = float(data.get('temperature', 0.9))  # 0.9로 조정
        
        # DB 사용 여부 (on/off)
        use_db = data.get('db', False)  # 기본값: off
        db_focus = 100 if use_db else 0
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        print(f"\n[JNext v2] User: {user_message}")
        print(f"[JNext v2] Project: {project_id or '일반 대화'}")
        print(f"[JNext v2] Temperature: {temperature}")
        print(f"[JNext v2] DB: {'🟢 ON' if use_db else '⚫ OFF'}")
        print(f"[JNext v2] Model: {model}")
        
        # 1. 사용자 메시지 즉시 저장 (백업)
        chat_id = save_chat_history(
            role='user',
            content=user_message,
            mode='v2',
            model=model,
            temperature=temperature,
            db_focus=db_focus,
            project_context=project_id
        )
        
        # 2. 대화 기록 로드 (모바일 AI 수준으로 확장)
        conversation_history = load_chat_history(limit=100)
        
        # 3. 프로젝트 정보 가져오기
        project = None
        project_db_context = ""
        project_prompt = ""
        
        if project_id:
            project = project_manager.get_project(project_id)
            if project:
                project_prompt = project.get_system_prompt()
                
                # DB Focus가 0%보다 클 때만 DB Context 가져오기
                if db_focus > 0:
                    # 사용자 메시지에서 키워드 추출 (특수문자 제거)
                    # "하이노워밍팔돌리기가 뭐지" → "하이노워밍팔돌리기 뭐지"
                    keyword = re.sub(r'[?!.,\s]+', ' ', user_message).strip()
                    # 너무 길면 첫 50자만
                    if len(keyword) > 50:
                        keyword = keyword[:50]
                    
                    project_db_context = project.get_db_context(limit=100, keyword=keyword)
                    
                    print(f"[JNext v2] Project loaded: {project.display_name}")
                    if keyword:
                        print(f"[JNext v2] Keyword search: {keyword}")
                    print(f"[JNext v2] DB context length: {len(project_db_context)} chars")
                    print(f"[JNext v2] DB context preview: {project_db_context[:200]}...")
                else:
                    print(f"[JNext v2] Project loaded: {project.display_name} (DB Context: 0%)")
            else:
                print(f"[JNext v2] Warning: Project '{project_id}' not found")
        
        # 4. 동적 맥락 구성
        context = ContextManager.build_context(
            temperature=temperature,
            db_focus=db_focus,
            project_id=project_id,
            user_message=user_message,
            conversation_history=conversation_history,
            project_db_context=project_db_context,
            project_prompt=project_prompt
        )
        
        print(f"[JNext v2] Context weights: {context['weights']}")
        print(f"[JNext v2] Using Temperature: {context['temperature']}")
        
        # 5. AI 호출 (재시도 로직 포함)
        ai_response = None
        error_occurred = None
        
        for attempt in range(3):
            try:
                ai_response = call_ai_model(
                    model_name=model,
                    user_message=user_message,  # 현재 질문만 (맥락 제거)
                    system_prompt=context['system_prompt'],
                    db_context=project_db_context if db_focus > 0 else "",  # DB Context 직접 전달
                    mode='v2',
                    conversation_history=conversation_history,  # 🔥 대화 이력 전체 전달!
                    temperature=context['temperature']
                )
                break
                
            except Exception as e:
                error_occurred = e
                error_str = str(e)
                
                if '503' in error_str and attempt < 2:
                    import time
                    wait_time = 2 ** attempt
                    print(f"[JNext v2] Retry {attempt + 1}/3 after {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                break
        
        # 6. 응답 처리
        if ai_response:
            ai_answer = ai_response.get('answer', '')
            
            # 마크다운 제거
            ai_answer_clean = remove_markdown_formatting(ai_answer)
            ai_response['answer'] = ai_answer_clean
            
            # AI 응답 저장
            save_chat_history(
                role='assistant',
                content=ai_answer_clean,
                mode='v2',
                model=model,
                temperature=temperature,
                db_focus=db_focus,
                project_context=project_id
            )
            
            # Phase 3: 프로젝트 대화이면 가치 평가 및 RAW 저장
            if project_id:
                try:
                    from .raw_storage import evaluate_chat_value, analyze_and_save_raw
                    
                    print(f"[JNext v2] RAW 저장 시도: project_id={project_id}")
                    
                    # 2단계: 가치 평가 (관대하게)
                    is_valuable = evaluate_chat_value(user_message, ai_answer)
                    
                    if is_valuable:
                        # 3단계: AI 분석 후 RAW 저장
                        analyze_and_save_raw(
                            project_id=project_id,
                            user_message=user_message,
                            ai_response=ai_answer_clean,
                            chat_ref=chat_id,
                            model=model
                        )
                        print(f"[JNext v2] RAW 저장 완료: {project_id}")
                    else:
                        print(f"[JNext v2] 잡담으로 판단, RAW 저장 스킵")
                except Exception as e:
                    import traceback
                    print(f"[JNext v2] RAW 저장 실패: {e}")
                    print(traceback.format_exc())
            
            return JsonResponse({
                'status': 'success',
                'response': ai_response,
                'context_info': {
                    'project': project.display_name if project else '일반 대화',
                    'db_focus': db_focus,
                    'temperature': temperature,
                    'weights': context['weights']
                },
                'model': model
            })
        else:
            error_msg = f"AI 서비스 일시 중단 중입니다. ({str(error_occurred)[:100]})"
            save_chat_history(
                role='assistant',
                content=error_msg,
                mode='v2',
                model=model,
                temperature=temperature,
                db_focus=db_focus,
                project_context=project_id
            )
            
            return JsonResponse({
                'status': 'error',
                'message': error_msg,
                'response': {
                    'answer': error_msg,
                    'claims': [],
                    'evidence': [],
                    'confidence': 0.0
                }
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"[JNext v2] Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def save_to_raw_v2(request):
    """
    RAW 컬렉션에 저장
    프로젝트별 저장
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project', 'hino')
        content = data.get('content', '')
        category = data.get('category', '')
        title = data.get('title', '')
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        # 프로젝트 정보
        project = project_manager.get_project(project_id)
        if not project:
            return JsonResponse({'error': f'Project not found: {project_id}'}, status=404)
        
        # RAW 컬렉션에 저장
        db = firestore.client()
        collection_name = project.get_collection_name('raw')
        
        doc_data = {
            project.get_field_name('category'): category,
            project.get_field_name('title'): title,
            project.get_field_name('content'): content,
            project.get_field_name('created_at'): now_kst(),
            project.get_field_name('status'): 'RAW',
            'project_id': project_id
        }
        
        doc_ref = db.collection(collection_name).add(doc_data)
        doc_id = doc_ref[1].id
        
        print(f"[JNext v2] Saved to {collection_name}: {doc_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'{collection_name}에 저장되었습니다.',
            'doc_id': doc_id,
            'collection': collection_name
        })
        
    except Exception as e:
        print(f"[JNext v2] Save error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def chat_v2_ui(request):
    """JNext v2 UI 렌더링"""
    
    # 프로젝트 목록 가져오기
    projects = project_manager.list_projects()
    
    return render(request, 'chat_v2.html', {
        'projects': projects
    })


def test_context_manager(request):
    """Context Manager 테스트 페이지"""
    
    # 테스트 데이터
    test_cases = []
    
    for focus in [0, 25, 50, 75, 100]:
        context = ContextManager.build_context(
            focus=focus,
            project_id='hino',
            user_message='테스트 질문',
            conversation_history=[],
            project_db_context='[DB 컨텍스트]',
            project_prompt='[프로젝트 프롬프트]'
        )
        
        test_cases.append({
            'focus': focus,
            'weights': context['weights'],
            'temperature': context['temperature']
        })
    
    return JsonResponse({
        'test_cases': test_cases
    })


@csrf_exempt
def list_projects(request):
    """
    프로젝트 목록 조회 API
    GET /api/v2/projects/
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    projects = project_manager.list_projects()
    
    return JsonResponse({
        'status': 'success',
        'projects': [
            {'id': pid, 'name': name}
            for pid, name in projects.items()
        ]
    })


@csrf_exempt
def create_project(request):
    """
    새 프로젝트 생성 API
    POST /api/v2/projects/create/
    
    Body:
        - project_id: 프로젝트 ID (영문소문자+언더스코어)
        - display_name: 표시 이름
        - description: 설명 (옵션)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"[DEBUG] 받은 데이터: {data}")
        project_id = data.get('project_id', '').strip()
        display_name = data.get('display_name', '').strip()
        description = data.get('description', '').strip()
        print(f"[DEBUG] project_id: '{project_id}', display_name: '{display_name}'")
        
        if not project_id or not display_name:
            return JsonResponse({
                'status': 'error',
                'message': 'project_id와 display_name은 필수입니다'
            }, status=400)
        
        # ID 유효성 검사 (영문소문자+언더스코어만)
        if not re.match(r'^[a-z_]+$', project_id):
            return JsonResponse({
                'status': 'error',
                'message': 'project_id는 영문 소문자와 언더스코어만 사용 가능합니다'
            }, status=400)
        
        # 프로젝트 생성
        new_project = project_manager.create_project(
            project_id=project_id,
            display_name=display_name,
            description=description
        )
        
        print(f"[ProjectManager] 새 프로젝트 생성: {project_id} ({display_name})")
        
        return JsonResponse({
            'status': 'success',
            'message': f'프로젝트 "{display_name}" 생성 완료',
            'project': {
                'id': new_project.project_id,
                'name': new_project.display_name,
                'description': new_project.description
            }
        })
        
    except Exception as e:
        print(f"[프로젝트 생성 실패] {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def document_manager_ui(request):
    """문서 관리 UI 렌더링"""
    projects = project_manager.list_projects()
    return render(request, 'document_manager.html', {
        'projects': projects
    })


@csrf_exempt
def search_documents(request):
    """
    문서 검색 API - 간소화 버전
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    try:
        project_id = request.GET.get('project', '').strip()
        collection = request.GET.get('collection', 'raw').strip()
        keyword = request.GET.get('keyword', '').strip()
        search_type = request.GET.get('search_type', 'all').strip()
        
        print(f"[검색] project={project_id}, collection={collection}, keyword={keyword}, search_type={search_type}")
        
        if not project_id:
            return JsonResponse({'error': 'project required'}, status=400)
        
        # Firestore에서 직접 가져오기
        db = firestore.client()
        
        # '전체' 컬렉션이면 raw, draft, final 모두 검색
        collections_to_search = []
        if collection in ['전체', 'all', '']:
            collections_to_search = ['raw', 'draft', 'final']
        else:
            collections_to_search = [collection]
        
        results = []
        
        for coll_name in collections_to_search:
            try:
                # projects/hinobalance/raw, draft, final 각각 검색
                docs_ref = db.collection('projects').document(project_id).collection(coll_name)
                docs = docs_ref.limit(50).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    
                    # 모든 가능한 필드명 시도 (우선순위 순서)
                    title = (data.get('제목') or data.get('title') or 
                            data.get('exercise_name') or data.get('doc_id') or 
                            doc.id)
                    
                    # 내용 필드 우선순위
                    content = (data.get('final_refined') or  # 최종 정제본
                              data.get('refined') or         # 정제본
                              data.get('organized_content') or  # 정리된 내용
                              data.get('content') or         # 기본 내용
                              data.get('정리본') or
                              data.get('ai_응답') or
                              data.get('내용') or
                              data.get('전체글') or
                              data.get('요약') or
                              '')
                    
                    # content가 boolean이면 문자열로 변환
                    if isinstance(content, bool):
                        content = ''
                    elif not isinstance(content, str):
                        content = str(content)
                    
                    # 원본 내용 (J님 입력)
                    original = (data.get('J님원본') or 
                               data.get('원본') or
                               data.get('original_content') or
                               data.get('원본질문') or
                               '')
                    
                    # original도 boolean 체크
                    if isinstance(original, bool):
                        original = ''
                    elif not isinstance(original, str):
                        original = str(original)
                    
                    # 카테고리와 운동명
                    category = data.get('카테고리') or data.get('category') or ''
                    exercise_name = data.get('exercise_name') or data.get('제목') or title or ''
                    keywords = data.get('키워드') or ''
                    
                    # 키워드가 리스트면 문자열로 변환
                    if isinstance(keywords, list):
                        keywords = ' '.join(keywords)
                    elif not isinstance(keywords, str):
                        keywords = str(keywords)
                    
                    # 검색 타입에 따라 필터링
                    if keyword:
                        match = False
                        keyword_lower = keyword.lower()
                        
                        if search_type == 'category':
                            # 카테고리 검색
                            match = keyword_lower in category.lower()
                        elif search_type == 'exercise':
                            # 운동명 검색
                            match = keyword_lower in exercise_name.lower()
                        elif search_type == 'keyword':
                            # 키워드 필드 검색
                            match = keyword_lower in keywords.lower()
                        else:  # 'all'
                            # 전체 검색 (제목, 내용, 카테고리, 운동명, 키워드)
                            match = (keyword_lower in title.lower() or 
                                    keyword_lower in content.lower() or
                                    keyword_lower in category.lower() or
                                    keyword_lower in exercise_name.lower() or
                                    keyword_lower in keywords.lower())
                        
                        if not match:
                            continue
                    
                    results.append({
                        'id': doc.id,
                        'collection': coll_name,  # 실제 컬렉션 이름
                        '제목': title,
                        '내용': content[:200] + '...' if len(content) > 200 else content,
                        '내용전체': content,
                        'J님원본': original,
                        '생성일': str(data.get('생성일') or data.get('작성일시') or data.get('created_at') or data.get('timestamp') or ''),
                        'ai모델': data.get('ai모델') or data.get('모델') or data.get('model') or '',
                        '품질점수': data.get('품질점수', 0),
                        '검증필요': data.get('검증필요', False),
                        'category': data.get('카테고리') or data.get('category') or '',
                        'exercise_name': data.get('exercise_name') or '',
                        '요약': data.get('요약') or '',
                        '키워드': data.get('키워드') or ''
                    })
                    
            except Exception as e:
                print(f"[검색] {coll_name} 컬렉션 오류: {e}")
                continue
        
        print(f"[검색] 완료: {len(results)}개")
        
        return JsonResponse({
            'status': 'success',
            'documents': results,
            'count': len(results)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_document(request):
    """
    문서 수정 API
    POST /api/v2/documents/update/
    
    Body:
        {
            "project": "hinobalance",
            "collection": "raw",
            "doc_id": "abc123",
            "updates": {
                "제목": "새 제목",
                "내용": "새 내용"
            }
        }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        collection = data.get('collection')
        doc_id = data.get('doc_id')
        updates = data.get('updates', {})
        
        if not all([project_id, collection, doc_id]):
            return JsonResponse({'error': 'project, collection, doc_id required'}, status=400)
        
        # 마크다운 제거 함수
        def remove_markdown(text):
            if not isinstance(text, str):
                return text
            # ** 제거
            text = text.replace('**', '')
            # ## 제거
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            return text
        
        # updates의 모든 텍스트 필드에서 마크다운 제거
        cleaned_updates = {}
        for key, value in updates.items():
            if isinstance(value, str):
                cleaned_updates[key] = remove_markdown(value)
            else:
                cleaned_updates[key] = value
        
        # Firestore 업데이트
        db = firestore.client()
        doc_ref = db.collection('projects').document(project_id).collection(collection).document(doc_id)
        
        # 수정일시 추가
        cleaned_updates['수정일시'] = now_kst()
        
        doc_ref.update(cleaned_updates)
        
        print(f"[문서 수정] projects/{project_id}/{collection}/{doc_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': '문서가 수정되었습니다.'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def regenerate_document(request):
    """
    문서 재생성 API
    POST /api/v2/documents/regenerate/
    
    Body:
        {
            "project": "hinobalance",
            "collection": "raw",
            "doc_id": "abc123"
        }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        collection = data.get('collection')
        doc_id = data.get('doc_id')
        
        if not all([project_id, collection, doc_id]):
            return JsonResponse({'error': 'project, collection, doc_id required'}, status=400)
        
        # 원본 문서 가져오기
        db = firestore.client()
        doc_ref = db.collection('projects').document(project_id).collection(collection).document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return JsonResponse({'error': 'Document not found'}, status=404)
        
        doc_data = doc.to_dict()
        
        # 재생성 소스 우선순위: J님원본 > 내용 > 정리본
        user_original = (doc_data.get('J님원본') or 
                        doc_data.get('원본') or 
                        doc_data.get('original_content'))
        
        current_content = (doc_data.get('final_refined') or
                          doc_data.get('refined') or
                          doc_data.get('organized_content') or
                          doc_data.get('content') or
                          doc_data.get('정리본') or
                          doc_data.get('ai_응답') or
                          doc_data.get('내용'))
        
        # 둘 중 하나라도 있으면 재생성 가능
        source_text = user_original or current_content
        
        if not source_text:
            return JsonResponse({'error': '재생성할 내용이 없습니다 (J님원본 또는 내용 필요)'}, status=400)
        
        # 프로젝트 전체 맥락 가져오기 (고급 재생성)
        project = project_manager.get_project(project_id)
        system_prompt = project.get_system_prompt() if project else ""
        
        # RAW → DRAFT 정리 시: DB 100% + gemini-pro 사용
        if collection == 'raw':
            db_context = project.get_db_context(limit=100) if project else ""  # DB 100%
            model_to_use = 'gemini-pro'  # Pro 모델 고정
            print(f"[RAW→DRAFT 정리 모드] DB 100%, gemini-pro 사용")
        else:
            db_context = project.get_db_context(limit=30) if project else ""  # 일반 재생성은 30개
            model_to_use = 'gemini-pro'
        
        # AI로 재생성 (프로젝트 맥락 활용)
        prompt = f"""다음 내용을 프로젝트 전체 맥락을 고려하여 더 전문적으로 재분석해주세요:

{source_text}

더 구체적이고, 깊이 있고, 프로젝트와 연결된 분석을 해주세요.

**중요 규칙:**
- 마크다운 문법(**, ##, - 등) 절대 사용 금지
- 평문(plain text)으로만 작성
- 숫자 목록은 1. 2. 3. 형식만 사용
- 강조는 「」 또는 '' 사용"""
        
        ai_response = call_ai_model(
            model_name=model_to_use,  # RAW→DRAFT일 때 gemini-pro 사용
            user_message=prompt,
            system_prompt=system_prompt + "\n\n절대 규칙: 마크다운 문법(**, ##, -, ` 등) 사용 금지. 평문으로만 작성.",
            db_context=db_context,  # 프로젝트 전체 DB 맥락 제공
            mode='v2',
            conversation_history=[],
            temperature=0.85
        )
        
        new_content = ai_response.get('answer', '')
        
        # 마크다운 제거 (만약 AI가 무시했을 경우 대비)
        new_content = remove_markdown_formatting(new_content)
        
        # 바로 저장하지 않고 결과만 반환 (프론트에서 미리보기 + 피드백)
        print(f"[문서 재생성 미리보기] projects/{project_id}/{collection}/{doc_id}")
        
        # 제목 추출
        title = (doc_data.get('제목') or
                doc_data.get('title') or
                doc_data.get('exercise_name') or
                doc.id)
        
        return JsonResponse({
            'status': 'success',
            'message': '재생성 완료 (미저장)',
            'title': title,
            'new_content': new_content,
            'current_content': current_content,  # 기존 AI 응답
            'user_original': user_original or '',  # J님 원본
            'used_source': 'J님원본' if user_original else '기존내용'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def apply_regeneration(request):
    """
    재생성 결과 적용 API (피드백 반영 가능)
    POST /api/v2/documents/apply-regeneration/
    
    Body:
        {
            "project": "hinobalance",
            "collection": "raw",
            "doc_id": "abc123",
            "new_content": "재생성된 내용",
            "feedback": "J님이라는 표현 제거해주세요" (선택)
        }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        collection = data.get('collection')
        doc_id = data.get('doc_id')
        new_content = data.get('new_content')
        feedback = data.get('feedback', '').strip()
        
        if not all([project_id, collection, doc_id, new_content]):
            return JsonResponse({'error': 'project, collection, doc_id, new_content required'}, status=400)
        
        # 피드백이 있으면 AI로 한 번 더 개선
        if feedback:
            project = project_manager.get_project(project_id)
            system_prompt = project.get_system_prompt() if project else ""
            
            prompt = f"""다음 내용을 사용자 피드백을 **정확히** 반영하여 수정해주세요:

[현재 내용]
{new_content}

[사용자 피드백]
{feedback}

**피드백 이행 규칙 (절대 준수):**
1. 삭제/제거 명령: 해당 부분을 **완전히** 삭제 (설명 추가 금지)
   - "J님 제거" → 모든 "J님" 단어 삭제
   - "「」 제거" → 모든 「」 기호 삭제
   - "1번 항목 삭제" → 1번 항목 전체 제거
2. 수정 명령: 지시대로 **정확히** 수정
3. 추가 명령: 요청한 내용만 추가
4. **피드백에 없는 내용은 변경하지 말 것**

**출력 형식 규칙:**
- 마크다운 문법(**, ##, - 등) 절대 사용 금지
- 평문(plain text)으로만 작성
- 숫자 목록은 1. 2. 3. 형식만 사용
- 강조는 '' 사용 (「」 금지)

**중요: 피드백 명령만 수행하고 불필요한 설명 추가하지 말 것**"""
            
            ai_response = call_ai_model(
                model_name='gemini-pro',
                user_message=prompt,
                system_prompt=system_prompt + "\n\n절대 규칙: 사용자 피드백을 정확히 이행. 삭제 명령 시 완전 삭제. 마크다운 금지.",
                db_context="",
                mode='v2',
                conversation_history=[],
                temperature=0.3  # 낮은 temperature로 정확성 향상
            )
            
            final_content = ai_response.get('answer', new_content)
            
            # 마크다운 제거 (만약 AI가 무시했을 경우 대비)
            final_content = remove_markdown_formatting(final_content)
            
            print(f"[재생성 피드백 적용] {feedback[:50]}...")
        else:
            final_content = new_content
        
        # Firestore 업데이트
        db = firestore.client()
        doc_ref = db.collection('projects').document(project_id).collection(collection).document(doc_id)
        
        updates = {
            'content': final_content,
            '내용': final_content,
            '내용전체': final_content,
            'final_refined': final_content,
            'refined': final_content,
            'organized_content': final_content,
            '정리본': final_content,
            'ai_응답': final_content,
            '수정일시': now_kst(),
            '재생성': True,
            '재생성시각': now_kst()
        }
        
        if feedback:
            updates['마지막피드백'] = feedback
        
        doc_ref.update(updates)
        
        print(f"[재생성 적용] projects/{project_id}/{collection}/{doc_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': '재생성 내용이 적용되었습니다.',
            'final_content': final_content,
            'feedback_applied': bool(feedback)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def combine_documents(request):
    """
    여러 문서 정리/재구성 API
    POST /api/v2/documents/combine/
    
    Body:
        {
            "project": "hinobalance",
            "documents": [
                {"collection": "raw", "doc_id": "abc123"},
                {"collection": "draft", "doc_id": "def456"}
            ],
            "target": "draft",  // 저장할 컬렉션
            "title": "정리된 문서 제목"
        }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        documents = data.get('documents', [])
        target = data.get('target', 'draft')
        title = data.get('title', '정리된 문서')
        
        if not project_id or not documents:
            return JsonResponse({'error': 'project, documents required'}, status=400)
        
        # 문서들 가져오기
        db = firestore.client()
        source_docs = []
        
        for doc_info in documents:
            col = doc_info.get('collection')
            doc_id = doc_info.get('doc_id')
            
            doc_ref = db.collection('projects').document(project_id).collection(col).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_data = doc.to_dict()
                source_docs.append({
                    'collection': col,
                    'doc_id': doc_id,
                    '제목': doc_data.get('제목', ''),
                    '내용': doc_data.get('내용', ''),
                    'J님원본': doc_data.get('J님원본', '')
                })
        
        if not source_docs:
            return JsonResponse({'error': '유효한 문서가 없습니다'}, status=404)
        
        # AI로 종합
        combined_content = "\n\n=== 문서 구분선 ===\n\n".join([
            f"[문서 {idx+1}] {doc.get('제목', 'N/A')}\n\n{doc.get('내용', '')}"
            for idx, doc in enumerate(source_docs)
        ])
        
        prompt = f"""다음 {len(source_docs)}개 문서를 종합하여 하나의 완성된 문서로 정리해주세요:

{combined_content}

핵심 내용을 통합하고, 중복을 제거하며, 구조적으로 정리해주세요."""
        
        project = project_manager.get_project(project_id)
        system_prompt = project.get_system_prompt() if project else ""
        
        ai_response = call_ai_model(
            model_name='gemini-pro',
            user_message=prompt,
            system_prompt=system_prompt,
            db_context="",
            mode='v2',
            conversation_history=[],
            temperature=0.7
        )
        
        # 새 문서 저장
        new_doc = {
            '제목': title,
            '내용': ai_response.get('answer', ''),
            '원본문서수': len(source_docs),
            '생성일': now_kst(),
            '종류': '정리본',
            '원본문서': [f"{d['collection']}/{d['doc_id']}" for d in source_docs]
        }
        
        new_ref = db.collection('projects').document(project_id).collection(target).add(new_doc)
        new_doc_id = new_ref[1].id
        
        print(f"[문서 정리] {len(source_docs)}개 → projects/{project_id}/{target}/{new_doc_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'{len(source_docs)}개 문서가 정리되었습니다.',
            'doc_id': new_doc_id,
            'collection': target
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_documents(request):
    """
    선택한 문서들 삭제 API
    POST /api/v2/documents/delete/
    
    Body:
        {
            "project": "hinobalance",
            "documents": [
                {"collection": "raw", "doc_id": "abc123"},
                {"collection": "draft", "doc_id": "def456"}
            ]
        }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        documents = data.get('documents', [])
        
        if not project_id or not documents:
            return JsonResponse({'error': 'project, documents required'}, status=400)
        
        # 문서들 삭제
        db = firestore.client()
        deleted_count = 0
        errors = []
        
        for doc_info in documents:
            col = doc_info.get('collection')
            doc_id = doc_info.get('doc_id')
            
            try:
                doc_ref = db.collection('projects').document(project_id).collection(col).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    doc_ref.delete()
                    deleted_count += 1
                    print(f"[문서 삭제 성공] projects/{project_id}/{col}/{doc_id}")
                else:
                    print(f"[문서 없음] projects/{project_id}/{col}/{doc_id}")
            except Exception as e:
                error_msg = f"{col}/{doc_id}: {str(e)}"
                errors.append(error_msg)
                print(f"[문서 삭제 실패] {error_msg}")
        
        response_data = {
            'status': 'success',
            'message': f'{deleted_count}개 문서가 삭제되었습니다.',
            'deleted': deleted_count
        }
        
        if errors:
            response_data['warnings'] = errors
            response_data['message'] += f' ({len(errors)}개 실패)'
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def move_to_final(request):
    """
    문서를 FINAL 컬렉션으로 이동 API
    POST /api/v2/documents/move-to-final/
    
    Body:
        {
            "project": "hinobalance",
            "collection": "raw",  # 또는 "draft"
            "doc_id": "abc123"
        }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project')
        source_col = data.get('collection')
        doc_id = data.get('doc_id')
        
        if not all([project_id, source_col, doc_id]):
            return JsonResponse({'error': 'project, collection, doc_id required'}, status=400)
        
        # FINAL로 이미 이동된 문서는 스킵
        if source_col == 'final':
            return JsonResponse({'error': '이미 FINAL 컬렉션에 있는 문서입니다.'}, status=400)
        
        db = firestore.client()
        
        # 1. 원본 문서 가져오기
        source_ref = db.collection('projects').document(project_id).collection(source_col).document(doc_id)
        source_doc = source_ref.get()
        
        if not source_doc.exists:
            return JsonResponse({'error': '원본 문서를 찾을 수 없습니다.'}, status=404)
        
        doc_data = source_doc.to_dict()
        
        # 2. FINAL 스키마 필드 추가 (없으면)
        if '밈스토리' not in doc_data:
            doc_data['밈스토리'] = {
                '훅_0_3초': '',
                '전개_3_10초': '',
                '반전_10_15초': '',
                '클로징_15_20초': ''
            }
        
        if '밈이미지' not in doc_data:
            doc_data['밈이미지'] = {
                '프레임1_0초': '',
                '프레임2_3초': '',
                '프레임3_10초': '',
                '프레임4_15초': ''
            }
        
        if '밈자막' not in doc_data:
            doc_data['밈자막'] = {
                '상단': '',
                '중단': '',
                '하단': ''
            }
        
        if '숏스크립트' not in doc_data:
            doc_data['숏스크립트'] = ''
        
        if '전자책' not in doc_data:
            doc_data['전자책'] = {
                '장': '',
                '절': '',
                '순서': 0,
                '타입': '동작'
            }
        
        # 3. FINAL 컬렉션에 복사
        final_ref = db.collection('projects').document(project_id).collection('final').document(doc_id)
        final_ref.set(doc_data)
        
        # 4. 원본 삭제
        source_ref.delete()
        
        print(f"[FINAL 이동 성공] projects/{project_id}/{source_col}/{doc_id} → final/{doc_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'FINAL로 이동되었습니다.',
            'doc_id': doc_id,
            'exercise_name': doc_data.get('운동명', 'Unknown')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_image(request):
    """
    AI 이미지 생성 API
    POST /api/v2/images/generate/
    
    Body:
        {
            "project": "hinobalance",
            "doc_id": "abc123",
            "collection": "final",
            "prompt": "골반 돌리기 동작 설명 다이어그램",
            "style": "diagram",  # diagram/illustration/realistic
            "size": "1024x768"   # 1024x1024/1024x768/768x1024
        }
    """
    try:
        import os
        import base64
        from PIL import Image
        from io import BytesIO
        
        data = json.loads(request.body)
        project_id = data.get('project')
        doc_id = data.get('doc_id')
        collection = data.get('collection')
        prompt = data.get('prompt', '').strip()
        style = data.get('style', 'diagram')
        size = data.get('size', '1024x768')
        
        if not all([project_id, doc_id, prompt]):
            return JsonResponse({'error': 'project, doc_id, prompt required'}, status=400)
        
        # 스타일별 프롬프트 보강
        style_prompts = {
            'diagram': 'clear educational diagram, clean lines, professional, medical illustration style, labeled, technical drawing',
            'illustration': 'soft illustration, friendly, approachable, pastel colors, warm tones, cartoon style, welcoming',
            'realistic': 'photorealistic, high detail, professional photography, studio lighting, sharp focus'
        }
        
        enhanced_prompt = f"{prompt}, {style_prompts.get(style, '')}, high quality, professional, 4k resolution"
        
        print(f"[이미지 생성] 프롬프트: {enhanced_prompt}")
        print(f"[이미지 생성] 크기: {size}")
        
        # 1단계: 기존 캐릭터 이미지 스타일 분석 (Gemini Vision - 캐싱)
        character_style_prompt = ""
        
        # 캐시 확인 (메모리 캐싱)
        cache_key = 'hinobalance_character_style'
        if not hasattr(generate_image, '_style_cache'):
            generate_image._style_cache = {}
        
        if cache_key in generate_image._style_cache:
            character_style_prompt = generate_image._style_cache[cache_key]
            print(f"[캐릭터 스타일] 캐시 사용: {character_style_prompt[:50]}...")
        else:
            try:
                from django.conf import settings
                from google import genai
                from pathlib import Path
                
                # Gemini API 키
                gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')
                
                if gemini_key:
                    # meme_images 폴더 경로
                    meme_folder = Path(__file__).parent.parent.parent / 'meme_images'
                    
                    # J님, 아내 대표 이미지 찾기
                    j_image = None
                    
                    for img_file in meme_folder.glob('*.png'):
                        if not j_image:
                            j_image = img_file
                            break
                    
                    # 대표 이미지 1개만 분석 (1회만)
                    if j_image and j_image.exists():
                        print(f"[캐릭터 스타일 분석 - 최초 1회] {j_image.name}")
                        
                        # Gemini Vision으로 스타일 분석
                        client = genai.Client(api_key=gemini_key)
                        
                        with open(j_image, 'rb') as f:
                            image_data = f.read()
                        
                        # 이미지 분석 요청
                        vision_response = client.models.generate_content(
                            model='gemini-2.0-flash-exp',
                            contents=[
                                "이 이미지의 캐릭터 스타일을 DALL-E 이미지 생성 프롬프트용으로 간결하게 설명해주세요. (3D/2D, 색감, 얼굴 특징, 의상, 전체 분위기 등을 영어로 50단어 이내)",
                                image_data
                            ]
                        )
                        
                        character_style_prompt = vision_response.text.strip()
                        
                        # 캐시에 저장 (서버 재시작 전까지 유지)
                        generate_image._style_cache[cache_key] = character_style_prompt
                        print(f"[캐릭터 스타일 캐시 저장] {character_style_prompt}")
                        
            except Exception as style_error:
                print(f"[캐릭터 스타일 분석 스킵] {str(style_error)}")
        
        # 캐릭터 스타일 프롬프트에 추가
        if character_style_prompt:
            enhanced_prompt = f"{enhanced_prompt}, character style: {character_style_prompt}, consistent with existing character design"
        
        # 2단계: DALL-E 3 API 호출 (GPT = 진)
        try:
            import openai
            from django.conf import settings
            import requests
            
            # OpenAI API 키 가져오기
            api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY')
            
            if not api_key:
                raise Exception("OPENAI_API_KEY not found in settings or environment")
            
            print(f"[DALL-E] API 키 확인: {api_key[:20]}...")
            
            # OpenAI 클라이언트 초기화
            openai.api_key = api_key
            
            # DALL-E 3 크기 매핑
            dalle_size = '1024x1024'  # DALL-E 3는 정사각형만 지원
            if size == '1024x768':
                dalle_size = '1792x1024'  # 가로형
            elif size == '768x1024':
                dalle_size = '1024x1792'  # 세로형
            
            print(f"[DALL-E] 크기 변환: {size} → {dalle_size}")
            
            # DALL-E 3 이미지 생성
            response = openai.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=dalle_size,
                quality="standard",
                n=1
            )
            
            # 생성된 이미지 URL 가져오기
            image_url_temp = response.data[0].url
            print(f"[DALL-E] 임시 URL: {image_url_temp[:50]}...")
            
            # 이미지 다운로드
            img_response = requests.get(image_url_temp, timeout=30)
            img_response.raise_for_status()
            image_data = img_response.content
            
            print(f"[DALL-E 생성 성공] 크기: {len(image_data)} bytes")
                
        except Exception as e:
            print(f"[DALL-E API 오류] {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback: 에러 메시지 반환
            return JsonResponse({
                'status': 'error',
                'error': f'이미지 생성 실패: {str(e)}',
                'message': 'DALL-E API 오류가 발생했습니다. OpenAI API 키를 확인해주세요.',
                'prompt': prompt,
                'style': style,
                'size': size
            }, status=500)
        
        # Firebase Storage 업로드
        try:
            from google.cloud import storage
            import uuid
            
            # Storage 클라이언트 초기화 (서비스 계정 사용)
            service_account_path = os.path.join(os.path.dirname(__file__), '../../jnext-service-account.json')
            storage_client = storage.Client.from_service_account_json(service_account_path)
            
            # 버킷 이름 (J님이 개설한 Firebase Storage)
            bucket_name = 'jnext-e3dd9.firebasestorage.app'
            bucket = storage_client.bucket(bucket_name)
            
            # 파일명 생성 (UUID + 타임스탬프)
            timestamp = datetime.now(KST).strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            blob_path = f'images/{project_id}/{collection}/{doc_id}/{timestamp}_{unique_id}.png'
            
            blob = bucket.blob(blob_path)
            
            # 이미지 업로드
            blob.upload_from_string(
                image_data,
                content_type='image/png'
            )
            
            # Public URL 생성
            blob.make_public()
            image_url = blob.public_url
            
            print(f"[Firebase Storage 업로드 성공] {blob_path}")
            print(f"[Public URL] {image_url}")
            
        except Exception as storage_error:
            print(f"[Firebase Storage 오류] {str(storage_error)}")
            # Storage 오류 시 Base64 인코딩하여 반환
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/png;base64,{image_base64}"
            print("[Fallback] Base64 인코딩 사용")
        
        # 문서에 이미지 메타데이터 저장
        db = firestore.client()
        doc_ref = db.collection('projects').document(project_id).collection(collection).document(doc_id)
        doc_snapshot = doc_ref.get()
        
        if doc_snapshot.exists:
            doc_data = doc_snapshot.to_dict()
            images = doc_data.get('이미지목록', [])
            images.append({
                'url': image_url,
                'prompt': prompt,
                'style': style,
                'size': size,
                'created_at': datetime.now(KST).isoformat()
            })
            doc_ref.update({'이미지목록': images})
        
        return JsonResponse({
            'status': 'success',
            'message': '이미지가 생성되었습니다',
            'image_url': image_url,
            'prompt': prompt,
            'style': style,
            'size': size
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

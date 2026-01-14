"""
JNext v2 Views
동적 맥락 시스템 기반 채팅 API
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
import json

from .core.context_manager import ContextManager
from .projects.project_manager import project_manager
from .ai_service import call_ai_model
from .views import save_chat_history, load_chat_history, now_kst

# 한국 시간대
KST = timezone(timedelta(hours=9))


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
        model = data.get('model', 'gemini-pro')
        project_id = data.get('project', None)  # None = 일반 대화
        temperature = float(data.get('temperature', 0.85))  # 0.0-1.0
        db_focus = int(data.get('db_focus', 25))  # 0-100
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        print(f"\n[JNext v2] User: {user_message}")
        print(f"[JNext v2] Project: {project_id or '일반 대화'}")
        print(f"[JNext v2] Temperature: {temperature}")
        print(f"[JNext v2] DB Focus: {db_focus}%")
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
        
        # 2. 대화 기록 로드
        conversation_history = load_chat_history(limit=20)
        
        # 3. 프로젝트 정보 가져오기
        project = None
        project_db_context = ""
        project_prompt = ""
        
        if project_id:
            project = project_manager.get_project(project_id)
            if project:
                project_prompt = project.get_system_prompt()
                project_db_context = project.get_db_context(limit=100)
                print(f"[JNext v2] Project loaded: {project.display_name}")
                print(f"[JNext v2] DB context length: {len(project_db_context)} chars")
                print(f"[JNext v2] DB context preview: {project_db_context[:200]}...")
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
                    user_message=context['full_message'],
                    system_prompt=context['system_prompt'],
                    db_context="",  # 이미 full_message에 포함됨
                    mode='v2',
                    conversation_history=[],  # 이미 full_message에 포함됨
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
            
            # AI 응답 저장
            save_chat_history(
                role='assistant',
                content=ai_answer,
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
                    
                    # 2단계: 가치 평가 (관대하게)
                    is_valuable = evaluate_chat_value(user_message, ai_answer)
                    
                    if is_valuable:
                        # 3단계: AI 분석 후 RAW 저장
                        analyze_and_save_raw(
                            project_id=project_id,
                            user_message=user_message,
                            ai_response=ai_answer,
                            chat_ref=chat_id,
                            model=model
                        )
                        print(f"[JNext v2] RAW 저장 완료: {project_id}")
                    else:
                        print(f"[JNext v2] 잡담으로 판단, RAW 저장 스킵")
                except Exception as e:
                    print(f"[JNext v2] RAW 저장 실패: {e}")
            
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

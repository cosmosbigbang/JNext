# JNext 개선 방안 (우선순위별)

**작성일**: 2026-01-09  
**목적**: 프로토타입 → 실사용 안정화

---

## 🔴 Priority 1: 즉시 해결 (새벽 테스트 전)

### 1.1 웹 UI Static 파일 문제 완전 해결
**현재 상태**: Whitenoise 설정 완료, Render 배포 대기 중  
**확인 사항**:
- [ ] Render 배포 완료 확인
- [ ] https://jnext.onrender.com/chat/ 접속 시 chat.js 로드 확인
- [ ] 전송 버튼 클릭 정상 작동 확인
- [ ] 드롭다운 글씨 색상 정상 확인

**실패 시 대안**:
```python
# settings.py에 추가
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

### 1.2 에러 메시지 사용자 친화적 개선
**문제**: 서버 에러 시 "500 Internal Server Error" 만 표시  
**해결**:
```python
# backend/api/views.py - chat() 함수 수정
try:
    # ... AI 호출 코드
except Exception as e:
    return JsonResponse({
        'status': 'error',
        'message': f'AI 응답 생성 실패: {str(e)}',
        'action': 'ERROR',
        'details': '잠시 후 다시 시도해주세요.'
    }, status=500)
```

**적용 위치**:
- `backend/api/views.py` 라인 1040-1100 (chat 함수)
- `backend/api/ai_service.py` 라인 150-200 (Gemini 호출)

### 1.3 로딩 상태 개선
**모바일 앱**: 
```dart
// jnext_mobile/lib/main.dart
// _isLoading 상태 시 CircularProgressIndicator 표시
if (_isLoading)
  Container(
    alignment: Alignment.center,
    padding: EdgeInsets.all(20),
    child: CircularProgressIndicator(),
  )
```

**웹 UI**:
```javascript
// backend/static/chat.js
function setLoading(loading) {
    isLoading = loading;
    sendButton.disabled = loading;
    sendButton.innerHTML = loading ? '<div class="loading"></div>' : '전송';
}
```

---

## 🟡 Priority 2: 안정성 개선 (1주일 내)

### 2.1 데이터 검증 강화
**Firestore 저장 전 검증**:
```python
def validate_document(data):
    required_fields = ['title', 'category', 'content']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f'{field} 필드는 필수입니다')
    
    if len(data['title']) < 2:
        raise ValueError('제목은 2자 이상이어야 합니다')
    
    if len(data['content']) < 10:
        raise ValueError('내용은 10자 이상이어야 합니다')
    
    return True
```

### 2.2 Gemini API 재시도 로직
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gemini_with_retry(message, system_prompt):
    return GEMINI_CLIENT.models.generate_content(...)
```

### 2.3 로그 개선
```python
import logging

logger = logging.getLogger(__name__)

# views.py에서
logger.info(f"[Chat API] User message: {message[:50]}...")
logger.info(f"[Chat API] Mode: {mode}, Model: {model}")
logger.error(f"[Chat API Error] {str(e)}", exc_info=True)
```

### 2.4 Rate Limiting (과도한 요청 방지)
```python
# settings.py
INSTALLED_APPS += ['django_ratelimit']

# views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def chat(request):
    # ...
```

---

## 🟢 Priority 3: 기능 개선 (2주 내)

### 3.1 대화 히스토리 저장
**현재**: 세션 종료 시 대화 사라짐  
**개선**: Firestore에 대화 이력 저장
```python
# 새 컬렉션: chat_history
{
    'user_id': 'default',
    'timestamp': datetime.now(),
    'messages': [
        {'role': 'user', 'content': '...'},
        {'role': 'assistant', 'content': '...', 'mode': 'hybrid'}
    ],
    'session_id': 'uuid...'
}
```

### 3.2 문서 검색 개선
**현재**: Firestore 전체 스캔  
**개선**: 
- 카테고리별 인덱스 추가
- 키워드 기반 필터링
- 최신순/관련도순 정렬

### 3.3 통합 모드 강화
**현재**: DB + 대화 단순 결합  
**개선**:
- DB 데이터 요약 → Gemini에게 전달
- 대화 맥락 유지 (최근 3턴)
- 참조 문서 명시

```python
def build_hybrid_context(db_results, conversation_history):
    db_summary = summarize_documents(db_results)
    recent_chat = conversation_history[-3:]  # 최근 3턴
    
    context = f"""
    [DB 참조 데이터]
    {db_summary}
    
    [최근 대화]
    {format_conversation(recent_chat)}
    """
    return context
```

### 3.4 Export 기능
```python
# GET /api/v1/export/?format=markdown
def export_documents(request):
    format = request.GET.get('format', 'markdown')
    docs = get_all_documents()
    
    if format == 'markdown':
        return generate_markdown(docs)
    elif format == 'json':
        return JsonResponse({'documents': docs})
```

---

## 🔵 Priority 4: 최적화 (1달 내)

### 4.1 캐싱 추가
```python
from django.core.cache import cache

def search_firestore_cached(query):
    cache_key = f'search:{hash(query)}'
    result = cache.get(cache_key)
    
    if result is None:
        result = search_firestore(query)
        cache.set(cache_key, result, timeout=300)  # 5분
    
    return result
```

### 4.2 DB 쿼리 최적화
- Firestore Composite Index 생성
- 페이지네이션 추가 (한 번에 20개씩)

### 4.3 모바일 앱 최적화
- 이미지 캐싱
- 오프라인 모드 지원
- 푸시 알림 (새 문서 생성 시)

---

## 📋 새벽 테스트 체크리스트

### 배포 확인
- [ ] Render 서버 정상 작동 (`https://jnext.onrender.com/`)
- [ ] 웹 UI 정상 작동 (`https://jnext.onrender.com/chat/`)
- [ ] 모바일 앱 서버 연결 정상

### 기능 테스트 (각 모드별)

#### 📊 DB 모드
- [ ] "하이노이론 검색" → 문서 리스트 표시
- [ ] "밸런스 저장" + 내용 입력 → Draft 저장 확인
- [ ] "최종본 생성" → Final 저장 확인
- [ ] 문서 없을 때 "데이터 없음" 응답 확인

#### 🔀 통합 모드
- [ ] "하이노이론 설명해" → DB + 분석 통합 응답
- [ ] 대화 후 "정리해서 저장" → Draft 저장 확인
- [ ] DB 데이터 참조하여 응답하는지 확인

#### 💬 대화 모드
- [ ] "하이노철봉이 뭐야?" → 일반 지식 기반 응답
- [ ] "브레인스토밍하자" → 자유로운 대화
- [ ] DB 참조 안 하는지 확인

### 엣지 케이스
- [ ] 빈 메시지 전송 → 무시 또는 에러 메시지
- [ ] 긴 메시지 (1000자) → 정상 처리
- [ ] 연속 요청 (3번 빠르게) → 정상 응답
- [ ] 존재하지 않는 문서 삭제 → 적절한 에러 메시지
- [ ] 네트워크 끊김 시뮬레이션 → 타임아웃 메시지

### 성능 테스트
- [ ] 웹 UI 응답 시간 (< 3초)
- [ ] 모바일 앱 응답 시간 (< 3초)
- [ ] 문서 100개 검색 시 성능

---

## 🛠️ 즉시 적용 가능한 Quick Fixes

### Fix 1: 에러 핸들링 개선
**파일**: `backend/api/views.py`
**라인**: 1040-1100

```python
# 기존
except Exception as e:
    print(f"[Chat API Error] {e}")
    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# 개선
except google.genai.errors.ClientError as e:
    logger.error(f"[Gemini API Error] {e}")
    return JsonResponse({
        'status': 'error',
        'message': 'AI 서비스 일시적 오류입니다. 잠시 후 다시 시도해주세요.',
        'error_type': 'GEMINI_ERROR',
        'details': str(e) if DEBUG else None
    }, status=503)
except Exception as e:
    logger.error(f"[Chat API Error] {e}", exc_info=True)
    return JsonResponse({
        'status': 'error',
        'message': '서버 오류가 발생했습니다.',
        'error_type': 'SERVER_ERROR'
    }, status=500)
```

### Fix 2: 모바일 앱 타임아웃 메시지 개선
**파일**: `jnext_mobile/lib/main.dart`
**라인**: 80-85

```dart
// 개선
} on TimeoutException catch (_) {
  setState(() {
    _messages.add(ChatMessage(
      text: '⏱️ 서버 응답 시간 초과\n네트워크를 확인하거나 잠시 후 다시 시도해주세요.',
      isUser: false,
      timestamp: DateTime.now(),
    ));
  });
} on SocketException catch (_) {
  setState(() {
    _messages.add(ChatMessage(
      text: '📡 네트워크 연결 오류\n인터넷 연결을 확인해주세요.',
      isUser: false,
      timestamp: DateTime.now(),
    ));
  });
}
```

---

## 📊 테스트 데이터 준비

### 하이노이론 샘플 (10개)
```
제목: 하이노밸런스 기본 원리
카테고리: 하이노이론
내용: 하이노밸런스는 신체의 균형을 유지하는 핵심 원리로...

제목: 하이노워킹 5단계 프로세스
카테고리: 하이노워킹
내용: 1단계: 자세 확인, 2단계: 호흡 조절...
```

### 테스트 시나리오 (각 3회 이상)
1. 검색 → 저장 → 최종본 생성 (전체 플로우)
2. 대화 → 통합 모드 전환 → 정리 저장
3. DB 모드 전용 (저장/삭제/수정)

---

## 🎯 최종 목표 (2주 후)

- **안정성**: 에러율 < 1%
- **응답 속도**: 평균 < 2초
- **사용성**: 에러 발생 시 명확한 안내
- **데이터 품질**: 최종본 50개 이상 정리 완료

---

**작성자**: Claude (GitHub Copilot)  
**검토 필요**: 우선순위 1번 항목 먼저 적용 후 테스트

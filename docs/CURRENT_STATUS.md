# JNext 현재 작업 마무리 체크리스트

**일시**: 2026-01-09 저녁  
**다음 작업**: 새벽 데이터 입력 및 테스트

---

## ✅ 완료된 작업

### 백엔드
- [x] Django 6.0 + Firestore 연동
- [x] Gemini AI 통합 (JSON 스키마 강제)
- [x] 3모드 시스템 (DB/통합/대화)
- [x] Render 배포 설정 (render.yaml)
- [x] Whitenoise 추가 (static 파일 서빙)

### 프론트엔드
- [x] Flutter 모바일 앱 (3모드 드롭다운)
- [x] 웹 UI (chat.html, chat.js)
- [x] 앱 아이콘 생성 (Purple gradient J)
- [x] UI 라인 간격 축소

### 배포
- [x] GitHub 저장소 동기화
- [x] Render 서버 배포
- [x] 환경 변수 설정 (Gemini API, Firebase)
- [x] Secret Files 설정 (Firebase JSON)

---

## 🔄 진행 중 (확인 필요)

### Render 최신 배포
- [ ] **커밋**: `1a2024a` (Add whitenoise for static files + fix dropdown text color)
- [ ] **배포 상태**: Events 탭에서 "Deploy live" 확인
- [ ] **예상 시간**: 2-3분 소요

### 확인 방법
1. https://dashboard.render.com → JNext 서비스
2. Events 탭 → 최신 배포 "Deploy live" 확인
3. Logs 탭 → `collectstatic` 명령 실행 확인

---

## 🧪 새벽 테스트 전 최종 확인

### 1. Render 배포 완료 확인
```bash
# 브라우저에서 확인
https://jnext.onrender.com/
https://jnext.onrender.com/chat/
```

**기대 결과**:
- 루트: `{"message": "JNext Backend API", ...}` JSON 응답
- 웹 UI: 채팅 인터페이스 정상 표시
- 콘솔 에러 없음

### 2. Static 파일 로드 확인
**브라우저 개발자 도구** (F12):
- Network 탭 → `/static/chat.js` 200 OK
- Console 탭 → 에러 없음

### 3. 모바일 앱 서버 연결 확인
```dart
// main.dart에서 확인
final String _apiUrl = 'https://jnext.onrender.com/api/v1/chat/';
```

**테스트**:
- 앱에서 "안녕" 전송 → 응답 확인
- 3가지 모드 전환 테스트

---

## 🚨 트러블슈팅

### 웹 UI 버튼 클릭 안 됨
**원인**: chat.js 로드 실패  
**확인**: 브라우저 콘솔에서 `404 /static/chat.js` 에러  
**해결**:
1. Render 배포 완료 대기
2. 브라우저 강력 새로고침 (Ctrl+Shift+R)
3. 여전히 안 되면:
   ```python
   # settings.py
   STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
   ```

### 모바일 앱 500 에러
**원인**: Gemini API 키 또는 Firebase 설정  
**확인**: Render Logs에서 에러 메시지 확인  
**해결**:
- Gemini API 키 재확인
- Firebase Secret File 경로 확인

### 드롭다운 글씨 안 보임
**해결 완료**: CSS 수정됨 (option { color: #333; })  
**확인**: 배포 후 새로고침

---

## 📋 새벽 테스트 준비물

### 데이터
- 하이노이론 텍스트 10개 이상
- 다양한 카테고리 (하이노이론/워킹/스케이팅/철봉/기본)

### 테스트 시나리오
1. **DB 모드**: "하이노이론 검색" → 저장 → 최종본 생성
2. **통합 모드**: "하이노밸런스 설명해" → 정리 저장
3. **대화 모드**: "브레인스토밍" → 자유 대화

### 성능 측정
- 응답 시간 (목표: < 3초)
- 에러 발생률
- UI 반응성

---

## 🎯 내일 아침 목표

### 정량적
- [ ] 문서 30개 이상 저장
- [ ] 최종본 10개 이상 생성
- [ ] 에러 없이 50회 이상 대화

### 정성적
- [ ] 3모드 차이 명확히 체감
- [ ] 통합 모드 유용성 확인
- [ ] UI/UX 개선점 메모

---

## 💾 백업 계획

### 로컬 백업
```bash
# Firestore 데이터 export (필요 시)
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Render 백업
- GitHub에 모든 코드 푸시 완료 ✅
- Render는 GitHub에서 자동 배포

---

## 📞 긴급 상황 대응

### 서버 다운 시
1. Render 대시보드 → Manual Deploy
2. 로컬 서버 실행:
   ```bash
   cd C:\Projects\JNext\backend
   .\venv\Scripts\Activate.ps1
   python manage.py runserver 0.0.0.0:8000
   ```
3. 모바일 앱 URL 임시 변경 → 로컬 IP

### Firebase 연결 끊김
- Service account JSON 파일 재확인
- Render Secret Files 재등록

---

## ✨ 성공 기준

**완벽한 성공**:
- 웹 UI 정상 작동 ✅
- 모바일 앱 정상 작동 ✅
- 50회 대화 에러 0건 ✅
- 데이터 30개 저장 완료 ✅

**최소 성공**:
- 웹 또는 앱 중 하나 정상 작동
- 10회 대화 성공
- 데이터 10개 저장

---

**현재 시각**: 저녁  
**다음 작업 시각**: 새벽  
**예상 소요 시간**: 2-3시간

J님, 푹 쉬세요! 새벽에 완벽하게 작동할 거예요! 🚀

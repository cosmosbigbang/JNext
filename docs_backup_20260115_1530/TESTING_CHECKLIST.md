# JNext v2 오후 테스트 체크리스트

## 📋 테스트 순서

### 1단계: 서버 시작
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**확인사항**:
- [ ] 서버 정상 시작 (포트 8000)
- [ ] 에러 메시지 없음

---

### 2단계: 웹 UI 테스트
브라우저: `http://localhost:8000/chat/v2/`

**듀얼 슬라이더 확인**:
- [ ] Temperature 슬라이더 표시됨 (기본값 85)
- [ ] DB Focus 슬라이더 표시됨 (기본값 25%)
- [ ] 슬라이더 값 표시가 실시간 업데이트

**프로젝트 전환 테스트**:
1. [ ] 프로젝트 선택 = "대화" → DB 슬라이더 25% 유지
2. [ ] 프로젝트 선택 = "하이노밸런스" → DB 슬라이더 50% 자동 전환
3. [ ] 다시 "대화"로 변경 → DB 슬라이더 25% 복귀

**대화 테스트**:
- [ ] 메시지 전송 정상 작동
- [ ] AI 응답 수신됨
- [ ] 대화 히스토리 유지

---

### 3단계: 자동 테스트 실행
```powershell
python test_v2_complete.py
```

**테스트 결과 확인**:
- [ ] Test 1: 듀얼 슬라이더 파라미터 전송 ✅
- [ ] Test 2: 3-Stage Storage (RAW 저장) ✅
- [ ] Test 3: Hierarchical 쿼리 ✅
- [ ] Test 4: AI 자기언급 제거 ✅
- [ ] Test 5: ProjectManager ✅
- [ ] Test 6: chat_history 스키마 ✅

---

### 4단계: Firestore 수동 확인
Firebase Console 접속

**확인 경로**:
1. [ ] `chat_history` 컬렉션:
   - temperature 필드 존재 (0.0-1.0)
   - db_focus 필드 존재 (0-100)
   - project_context 필드 존재
   - raw_분석_완료 필드 존재
   - raw_저장_위치 필드 존재

2. [ ] `projects/hinobalance` 문서:
   - display_name: "하이노밸런스"
   - collections: ["raw", "draft", "final", "theory"]

3. [ ] `projects/hinobalance/raw` 서브컬렉션:
   - 문서 개수 확인 (39개 이상)
   - 최신 문서 확인:
     * 제목 필드
     * 키워드 필드
     * 카테고리 필드
     * 요약 필드
     * AI 자기언급 없음 확인

4. [ ] `projects/hinobalance/draft` 서브컬렉션:
   - 문서 개수 확인 (31개 이상)

---

### 5단계: RAW 저장 수동 테스트
웹 UI에서:

1. [ ] 프로젝트를 "하이노밸런스" 선택
2. [ ] Temperature: 85, DB: 50% 확인
3. [ ] 메시지 입력: "하이노워킹 전진 동작의 핵심 포인트는?"
4. [ ] 전송 후 5초 대기
5. [ ] Firestore에서 `projects/hinobalance/raw` 확인
6. [ ] 새 문서 추가됨 확인
7. [ ] 제목, 키워드, 카테고리, 요약 필드 정상
8. [ ] AI 자기언급("제가", "저는", "젠", "클로" 등) 없음 확인

---

### 6단계: 구형 컬렉션 삭제
**⚠️ 위 모든 테스트 통과 후에만 실행**

```powershell
python migrate_firestore.py
# 옵션 2 선택 (Delete old collections)
```

**삭제 대상**:
- [ ] hino_raw
- [ ] hino_draft
- [ ] hino_final
- [ ] hino_theory

**삭제 확인**:
- [ ] Firestore Console에서 위 컬렉션 사라짐
- [ ] projects/hinobalance/* 서브컬렉션은 유지됨

---

### 7단계: 최종 검증
웹 UI 재테스트:

1. [ ] 서버 재시작
2. [ ] 프로젝트 선택 정상 작동
3. [ ] 대화 기능 정상
4. [ ] 슬라이더 동작 정상
5. [ ] RAW 저장 정상

---

## 🐛 문제 발생 시

### Temperature 슬라이더 안 보임
- `chat_v2.html` 파일 확인
- 브라우저 캐시 삭제 (Ctrl+F5)

### DB 슬라이더 자동 전환 안 됨
- 브라우저 콘솔 확인 (F12)
- JavaScript 에러 확인

### RAW 저장 안 됨
1. 서버 콘솔 확인
2. `raw_storage.py` 에러 로그 확인
3. Firestore 권한 확인 (jnext-service-account.json)

### API 에러 (500)
1. 서버 콘솔에서 traceback 확인
2. collection 경로 오류 가능성 확인
3. `views.py` 또는 `views_v2.py` 로그 확인

### 마이그레이션 후 데이터 안 보임
1. Firestore Console에서 경로 확인:
   - 잘못된: `hino_raw/{doc_id}`
   - 올바른: `projects/hinobalance/raw/{doc_id}`
2. 롤백 필요 시: 구형 컬렉션 아직 존재 (백업됨)

---

## 📊 성공 기준

✅ **필수 (P0)**:
- 듀얼 슬라이더 정상 작동
- 프로젝트 전환 시 DB 슬라이더 자동 조정
- 대화 기능 정상
- RAW 저장 정상
- Hierarchical 쿼리 정상

✅ **권장 (P1)**:
- 자동 테스트 6개 모두 통과
- AI 자기언급 완전 제거
- 구형 컬렉션 삭제 완료

✅ **선택 (P2)**:
- theory 서브컬렉션 삭제
- Mobile app 테스트
- Render 배포

---

**작성**: Claude (Copilot Agent)  
**날짜**: 2026-01-14  
**용도**: J님 오후 테스트 가이드

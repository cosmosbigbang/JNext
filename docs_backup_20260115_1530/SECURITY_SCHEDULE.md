# JNext 보안 점검 스케줄

**작성일**: 2026-01-13
**설정자**: J님

---

## 📅 정기 보안 점검

### 스케줄
- **빈도**: 매일 1회
- **시간**: 오후 11시 (KST, UTC+9)
- **UTC 시간**: 14:00 UTC
- **담당**: Claude (클로)

---

## 🔍 점검 항목

### 1. Git 저장소 점검
```bash
# .gitignore 확인
cat .gitignore

# 서비스 계정 파일 커밋 이력 확인
git log --all --full-history --source -- "*service-account.json"

# 현재 상태 확인
git status
```

### 2. 민감 파일 위치 확인
```bash
# 서비스 계정 파일이 루트에만 존재하는지
Test-Path "c:\Projects\JNext\jnext-service-account.json"
Test-Path "c:\Projects\JNext\backend\jnext-service-account.json"

# .env 파일 확인
Get-ChildItem -Recurse -Filter "*.env" -File
```

### 3. 코드 내 하드코딩 검색
```bash
# API 키 패턴 검색
grep -r "AIza[0-9A-Za-z_-]{35}" **/*.py
grep -r "sk-[0-9A-Za-z]{48}" **/*.py
grep -r "GEMINI_API_KEY.*=" **/*.py
```

### 4. Render 환경변수 확인 (수동)
- [ ] FIREBASE_CREDENTIALS_PATH 설정됨
- [ ] GEMINI_API_KEY 설정됨
- [ ] SECRET_KEY 생성됨
- [ ] 하드코딩된 키 없음

### 5. 로컬 보안
- [ ] jnext-service-account.json이 루트에만 존재
- [ ] .gitignore에 모든 민감 파일 등록됨
- [ ] backup 파일에 API 키 없음

---

## ✅ 점검 완료 체크리스트

### 2026-01-13 (최초 설정)
- [x] .gitignore 설정 완료
- [x] 서비스 계정 파일 루트로 이동
- [x] Python 스크립트 경로 업데이트
- [x] Git 커밋 이력 클린
- [x] 비공개 저장소 확인

### 향후 점검 기록
**형식**: YYYY-MM-DD - 상태 - 이슈사항

```
2026-01-14 23:00 - [점검 예정]
```

---

## 🚨 보안 이슈 발생 시 대응

### 즉시 조치
1. 해당 파일/키 즉시 삭제
2. Git 히스토리에서 완전 제거 (git filter-branch)
3. 노출된 키 무효화 (Firebase/Google Cloud Console)
4. 새 키 발급 및 환경변수 업데이트

### 보고 대상
- J님에게 즉시 알림
- 이슈 내용 문서화

---

**참고**: Claude는 스케줄링 기능이 없으므로, J님이 매일 오후 11시에 "클로 보안 점검해"라고 요청하시면 위 항목들을 자동 실행합니다.

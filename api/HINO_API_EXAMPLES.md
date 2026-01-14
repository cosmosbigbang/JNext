# 하이노밸런스 자동화 API 테스트

## 1. 현황 조회
```bash
curl http://localhost:8000/api/v1/hino/status/
```

## 2. 카테고리 공통이론 생성
```bash
curl -X POST http://localhost:8000/api/v1/hino/auto/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "category_theory",
    "target": "하이노골반"
  }'
```

## 3. 개별 운동 상세 정리
```bash
curl -X POST http://localhost:8000/api/v1/hino/auto/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "organize",
    "target": "하이노워밍벤치"
  }'
```

## 4. 시트콤 시나리오 생성
```bash
curl -X POST http://localhost:8000/api/v1/hino/auto/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sitcom",
    "target": "하이노골반상하",
    "options": {
      "scene_type": "home"
    }
  }'
```

## 5. 문서 통합 (이론 통합)
```bash
curl -X POST http://localhost:8000/api/v1/hino/auto/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "integrate",
    "target": "하이노이론",
    "options": {
      "output_name": "하이노전체이론",
      "versions": ["summary", "medium", "full"]
    }
  }'
```

## 6. 자연어 명령 (향후 지원)
```bash
curl -X POST http://localhost:8000/api/v1/hino/auto/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "하이노골반 공통이론 만들어줘"
  }'
```

## PowerShell용

### 현황 조회
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/hino/status/" -Method GET
```

### 골반 공통이론 생성
```powershell
$body = @{
    action = "category_theory"
    target = "하이노골반"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/hino/auto/" -Method POST -Body $body -ContentType "application/json"
```

### 워밍벤치 상세 정리
```powershell
$body = @{
    action = "organize"
    target = "하이노워밍벤치"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/hino/auto/" -Method POST -Body $body -ContentType "application/json"
```

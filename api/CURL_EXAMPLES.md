# JNext Phase 2 - curl 테스트 명령어

## 1. CREATE (새 문서 생성)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "CREATE_OR_UPDATE",
    "collection": "test_users",
    "payload": {
      "data": {
        "name": "홍길동",
        "email": "hong@example.com",
        "age": 25
      }
    }
  }'
```

## 2. READ (전체 조회)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type": application/json" \
  -d '{
    "command": "READ",
    "collection": "test_users",
    "payload": {}
  }'
```

## 3. READ (특정 문서)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "READ",
    "collection": "test_users",
    "payload": {
      "document_id": "YOUR_DOCUMENT_ID"
    }
  }'
```

## 4. UPDATE (문서 업데이트)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "CREATE_OR_UPDATE",
    "collection": "test_users",
    "payload": {
      "document_id": "YOUR_DOCUMENT_ID",
      "data": {
        "age": 26,
        "status": "updated"
      }
    }
  }'
```

## 5. READ with FILTER (필터 조회)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "READ",
    "collection": "test_users",
    "payload": {
      "filters": {
        "status": "active"
      }
    }
  }'
```

## 6. DELETE (문서 삭제)
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -d '{
    "command": "DELETE",
    "collection": "test_users",
    "payload": {
      "document_id": "YOUR_DOCUMENT_ID"
    }
  }'
```

## API Key 사용 시
```bash
curl -X POST http://localhost:8000/api/v1/execute-command/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"command": "READ", "collection": "test_users", "payload": {}}'
```

## PowerShell 버전

### CREATE
```powershell
$body = @{
    command = "CREATE_OR_UPDATE"
    collection = "test_users"
    payload = @{
        data = @{
            name = "홍길동"
            email = "hong@example.com"
            age = 25
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/execute-command/" -Method POST -Body $body -ContentType "application/json"
```

### READ ALL
```powershell
$body = @{
    command = "READ"
    collection = "test_users"
    payload = @{}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/execute-command/" -Method POST -Body $body -ContentType "application/json"
```

### DELETE
```powershell
$body = @{
    command = "DELETE"
    collection = "test_users"
    payload = @{
        document_id = "YOUR_DOCUMENT_ID"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/execute-command/" -Method POST -Body $body -ContentType "application/json"
```

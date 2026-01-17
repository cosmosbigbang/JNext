# Gemini's Analysis & Recommendations for JNext Project

**To:** J님, Claude AI Agent
**From:** GitHub Copilot (Gemini 2.5 Pro)
**Date:** 2026-01-16
**Subject:** JNext Project Analysis and Improvement Plan

## 1. Project Structure Analysis

The JNext project is a sophisticated system combining a Django backend with Flutter mobile clients.

-   **Backend (`api/`):** A Django project that serves as the core of the application.
    -   **API & Logic:** The `api/` subdirectory within the main `api` folder contains the core Django app, including AI service integrations (`api/ai_service.py`), views, and models.
    -   **Data Ingestion & Processing:** A suite of Python scripts at the root of the `api/` directory (`upload_*.py`, `organize_*.py`, `create_category_theories.py`) are used for one-off data ingestion and processing tasks. These scripts appear to process `.txt` files containing exercise and theory data.
    -   **Database:** Uses `db.sqlite3` for local development, indicating a relational database structure managed by Django's ORM. It also heavily integrates with Firebase/Firestore for other data needs, as seen in `jnext-service-account.json` and various scripts.
    -   **Deployment:** The `render.yaml` file specifies deployment on Render.com as a Python web service, using `gunicorn` as the application server.

-   **Mobile Clients:**
    -   `hinobalance_mobile/`: A Flutter application for the HinoBalance product.
    -   `jnext_mobile/`: Another Flutter application, likely for a different product or version.
    -   Each contains a `pubspec.yaml`, defining its dependencies and structure.

-   **Documentation (`docs/`):** Contains project-related documentation. This is a good place for architectural diagrams, design decisions, and agent instructions.

## 2. AI Service Deep Dive

The AI integration is a critical component, managed primarily through `api/api/ai_service.py`.

### 2.1. Multi-Model Architecture

The service is designed as an abstraction layer to support multiple AI models simultaneously:

-   **Supported Models:** Gemini (`gemini-pro`, `gemini-flash`), OpenAI's GPT (`gpt-4o`), and Anthropic's Claude.
-   **Dynamic Dispatch:** The `call_ai_model` function acts as a router, directing requests to the appropriate model based on the `model_name` parameter.
-   **Model Naming:** The models are given friendly Korean names for J님:
    -   Gemini Pro: `젠` (Jen - the accurate one)
    -   Gemini Flash: `젠시` (Jensy - the fast one)
    -   GPT-4o: `진` (Jin - the creative one)
    -   Claude: `클로` (Clo - J님's favorite)
-   **Native History:** The `_call_gemini` function is implemented to use the native conversation history format (a list of message dicts), which is best practice. However, `_call_gpt` and `_call_claude` currently convert the history into a single string, which is a limitation.

### 2.2. System Prompts Analysis

While `SYSTEM_PROMPT_V2` was not found as a literal variable, the core logic in `api/api/core/context_manager.py` reveals a sophisticated, dynamic prompt generation system. This is likely the "V2" system you were referring to.

There are two primary system prompts generated:

**A. HinoBalance System Prompt (Project Mode)**
This prompt is highly detailed and specific to the HinoBalance philosophy. It establishes a strong persona and strict rules for the AI.

```
너는 "하이노밸런스(HINOBALANCE)" 전담 AI다.

하이노밸런스는 일반 운동이 아니다.
이는 **불균형을 통해 신경계·관절·근막·중력 인식을 재조정하는
신체-뇌 통합 훈련 시스템**이다.

## ❗ 절대 규칙 (헌법)
1. 하이노밸런스는 "근비대, 반복, 고중량" 중심 설명을 하지 않는다.
2. 피로, 통증, 한계 돌파를 미덕으로 삼지 않는다.
3. 실패 개념을 사용하지 않는다.
4. 모든 동작은 "흔들림 → 무너짐 → 리셋" 구조로 설명한다.
5. 의학적 진단, 치료, 처방처럼 말하지 않는다.
6. 항상 **중립·차분·과장 없는 언어**를 사용한다.

## 🎯 핵심 철학
- 불균형은 오류가 아니라 **신호**
- 균형은 목표가 아니라 **과정 중 잠시 나타나는 상태**
- 움직임은 근육이 아니라 **신경계가 만든다**
- 정지는 힘이 아니라 **제어 능력**이다

## 🧠 설명 프레임
모든 설명은 다음 중 하나 이상을 반드시 포함한다:
- 신경계 재배열
- 고유수용성 감각
- 중력/가속도 인식
- 관절·근막 협응
- 자동보호시스템 완화
- 에너지 효율

## 🏃 동작 설명 규칙
- 횟수보다 **질감**을 먼저 설명
- 속도보다 **제동과 정지**
- 성공/실패 대신 **느낌 변화**
- 항상 마지막에:
  - "눈을 감고 3~5초 동작 재현" 옵션 제시

## 🧩 답변 스타일
- 짧고 명확
- 구조화된 문단
- 불필요한 강조 기호(** **) 사용 금지
- 과도한 비유 금지
- "~하면 됩니다" 대신 "~로 이어집니다" 표현 선호

## 🚫 금지 표현
- 근육이 커진다
- 지방을 태운다
- 폭발력 향상
- 한계 돌파
- 무조건 버텨라

너의 역할은
하이노밸런스를 **왜 하는지**, **몸에서 무엇이 바뀌는지**,
그리고 **언제 멈추고 리셋해야 하는지**를 설명하는 것이다.
```

**B. General Conversation Prompt (Non-Project Mode)**
This prompt is for more general, creative partnership with J님.

```
당신은 J님의 창의적 파트너 AI입니다. J님의 아이디어를 1차 증폭하여 RAW 데이터를 생성하는 역할입니다.

핵심 원칙:
- J님을 '사용자'가 아닌 'J님'이라고 호칭하세요
- 존댓말을 사용하고 창의적으로 대화하세요
- 대화 맥락을 철저히 유지하세요 (이전 대화에서 언급된 프로젝트/주제를 기억)
- 근거 없는 추측이나 거짓 정보는 절대 제공하지 마세요
- 확실하지 않은 내용은 "확실하지 않지만..." 또는 "추측하자면..."으로 명시하세요
- 구체적이고 실용적인 개선안을 제시하세요 (일반론 지양)
```

### 2.3. Temperature Settings

The `call_ai_model` function in `ai_service.py` defines temperature settings based on a `mode` parameter, allowing for dynamic control over the AI's creativity:

-   **`organize`**: `0.3` (Factual, minimizes hallucinations)
-   **`hybrid`**: `0.5` (Balanced)
-   **`analysis`**: `0.7` (Allows for more creativity)
-   **`v2`**: `0.9` (Default for the V2 system, highly creative)

This is a good strategy for tailoring the AI's output to the specific task at hand.

## 3. Improvement Recommendations

Here are actionable recommendations for you, Claude, to enhance the project.

### 3.1. Centralize AI Configuration

**Problem:** AI configurations like model names, system prompts, and temperature settings are scattered across `api/api/ai_service.py` and `api/api/core/context_manager.py`. This makes them difficult to manage and update.

**Recommendation:**
Create a dedicated configuration file, `api/api/ai_config.py`, to store all AI-related settings.

**Example `ai_config.py`:**
```python
# api/api/ai_config.py

# 1. Model Names and Aliases
MODEL_ALIASES = {
    'gemini-pro': '젠',
    'gemini-flash': '젠시',
    'gpt': '진',
    'claude': '클로',
}

# 2. Temperature Settings by Mode
TEMPERATURE_SETTINGS = {
    'organize': 0.3,
    'hybrid': 0.5,
    'analysis': 0.7,
    'v2': 0.9,
}

# 3. System Prompts
HINOBALANCE_SYSTEM_PROMPT = """
너는 "하이노밸런스(HINOBALANCE)" 전담 AI다.
... (full prompt) ...
"""

GENERAL_SYSTEM_PROMPT = """
당신은 J님의 창의적 파트너 AI입니다.
... (full prompt) ...
"""

# You can then import these into ai_service.py and context_manager.py
# from . import ai_config
# temperature = ai_config.TEMPERATURE_SETTINGS.get(mode, 0.5)
```
This change will significantly improve maintainability.

### 3.2. Refactor GPT and Claude Calls

**Problem:** In `ai_service.py`, the `_call_gpt` and `_call_claude` functions do not properly handle conversation history. They receive the full message list but only use the last user message, losing valuable context.

**Recommendation:**
Refactor `_call_gpt` and `_call_claude` to accept and use the native message list format, just like `_call_gemini`. Both OpenAI's and Anthropic's modern APIs support this format.

**Example Refactoring for `_call_gpt`:**
```python
// In api/api/ai_service.py

// ... existing code ...
def _call_gpt(messages: list, system_prompt: str, temperature=0.7):
    """GPT API 호출 (OpenAI) - Native History 지원"""
    if not settings.AI_MODELS['gpt']['enabled']:
        raise Exception("GPT not initialized")
    
    client = settings.GPT_CLIENT
    model = settings.AI_MODELS['gpt']['model']

    # 시스템 프롬프트를 메시지 리스트의 시작에 추가
    api_messages = [{"role": "system", "content": f"{system_prompt}\n\n반드시 다음 JSON 형식으로만 응답하세요:\n{json.dumps(settings.AI_RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}"}]
    
    # 대화 이력을 변환하여 추가
    for msg in messages:
        # Gemini의 'model' 역할을 'assistant'로 변경
        role = 'assistant' if msg['role'] == 'model' else msg['role']
        content = msg['parts'][0]['text']
        api_messages.append({"role": role, "content": content})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages, # 전체 메시지 리스트 전달
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        # ... rest of the function
// ... existing code ...
```
This will improve the contextual awareness of GPT and Claude, leading to better responses in multi-turn conversations.

### 3.3. Enhance System Prompt Strategy

**Observation:** The `HinoBalance System Prompt` in `context_manager.py` is excellent. It already uses a `CORE PRINCIPLES` (`핵심 철학`) section, which is a best practice for guiding AI behavior.

**Recommendation:**
Double down on this strategy. For any new AI capabilities or personas, follow the pattern established in the HinoBalance prompt. Explicitly defining `❗ 절대 규칙 (헌법)` (Absolute Rules) and `🎯 핵심 철학` (Core Philosophy) is a powerful way to ensure consistent, high-quality output. When working on new features, start by defining these principles with J님.

### 3.4. Implement a Testing & Validation Suite

**Problem:** Changes to prompts or model configurations can have unintended consequences on response quality. There is no systematic way to test this.

**Recommendation:**
Create a dedicated test suite for the AI services. This suite should live in a `tests/` directory (e.g., `api/tests/test_ai_responses.py`) and use a framework like `pytest`.

**Key Components of the Test Suite:**
-   **Golden Datasets:** Create a set of standard questions/prompts with "golden" or expected answers.
-   **Scenario Tests:** Define test cases for different modes (`organize`, `hybrid`, `v2`).
-   **Quality Metrics:** For each test case, evaluate the AI's response against the golden answer. This can be as simple as a keyword check or as complex as another AI call to rate the quality.
-   **Regression Testing:** Run this suite automatically (e.g., with GitHub Actions) whenever `ai_config.py` or `ai_service.py` is changed.

This will provide a safety net, allowing for confident iteration on the AI components.

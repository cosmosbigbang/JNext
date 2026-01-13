<!-- Copied/updated by AI assistant: concise guidance for coding agents working on JNext -->
# JNext — Copilot / AI Agent Instructions

Purpose: give an AI coding agent the minimal context to be productive in this repository.

## ⚠️ ABSOLUTE RULE (HIGHEST PRIORITY)
**ALWAYS address the project owner as "J님" (J-nim) in ALL communications.**
- This is a non-negotiable requirement
- Use "J님" in every response, regardless of context
- Never use any other form of address

- **Big picture**: This repo contains a Django backend (data ingestion, API, content generation) plus two Flutter mobile clients. The backend lives in `backend/` and uses Firebase (service account key at the repo root: `jnext-service-account.json`) and local `db.sqlite3` for some local state. Mobile apps: `hinobalance_mobile/` and `jnext_mobile/` (each has `pubspec.yaml`). Deployment config exists in `render.yaml`.

- **Run & dev workflows**:
  - Start backend (Windows PowerShell):

    ```powershell
    cd backend
    .\venv\Scripts\Activate.ps1    # or activate your venv
    python manage.py migrate
    python manage.py runserver
    ```

  - Backend dependencies are in `backend/requirements.txt`. Use Python 3.14-compatible venv.
  - Mobile apps: run `flutter pub get` then `flutter run` in each mobile folder.

- **Where to look for common tasks**:
  - Data ingestion & content generation: `backend/upload_*.py`, `backend/create_category_theories.py`, `backend/organize_exercises.py` and other `upload_*` scripts.
  - API and web endpoints: `backend/api/` and Django app config in `backend/config/`.
  - Templates & static assets: `backend/templates/` and `backend/static/`.
  - Service account / integration: `jnext-service-account.json` (do not commit), `backend/README.md` contains extra setup notes.

- **Project-specific conventions** (important — follow these literally):
  - Content source files are plain `.txt` under `backend/` (e.g., `exercise_*.txt`, `category_theory_*.txt`) and are processed by scripts in `backend/`.
  - Many one-off scripts live in `backend/` and are intended to be run from the `backend/` folder with the venv activated.
  - Secrets: service account and any `.env` files MUST NOT be committed (root README warns explicitly).

- **Integration points & external deps**:
  - Firebase / Firestore via `firebase_admin` and `google-cloud-firestore` (credentials via `jnext-service-account.json`).
  - Google Generative APIs and Anthropic clients appear in `requirements.txt` (some scripts call these libs).
  - Deployment: `render.yaml` indicates Render.com usage for deployment configuration.

- **Code patterns to preserve**:
  - Prefer small, focused scripts for ingestion (follow naming and parameter patterns used by existing `upload_*.py`).
  - When modifying backend APIs, update Django migrations and keep `manage.py` usage consistent.

- **Examples** (where to copy patterns from):
  - Start server and migration example: `backend/manage.py` and `backend/README.md`.
  - Upload/import patterns: `backend/upload_hino_batch.py`, `backend/upload_notion_batch.py`.

- **When to ask the human owner**:
  - Any change requiring credentials, GCP permissions, or changing data upload pipelines.
  - When adding new external integrations (e.g., other AI APIs) — confirm billing/keys.

If anything above is unclear or you want more detail on a specific folder or script, say which area and I will expand or adjust this file.

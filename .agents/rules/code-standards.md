---
name: code-standards
description: "Coding conventions, style rules, and project organization standards for both backend (Python/FastAPI) and frontend (React/TypeScript)."
activation: Always On
---

# Code Standards

## Backend (Python)

| Standard | Rule |
|---|---|
| **Type Safety** | Type hints on ALL function signatures. Pydantic for data validation. |
| **Style** | PEP 8. Max 100 chars/line. f-strings only. |
| **Docs** | JSDoc for functions. Docstrings on public functions/classes. Comments explain "why" not "what". |
| **Imports** | Absolute imports only (`from backend.agents.specialist...`). |
| **Tests** | ALL tests in `backend/tests/`. Standard Pytest. Use `unittest.mock` to isolate from APIs. |
| **Dependencies** | Listed in `requirements.txt`. Always use `.venv`. |
| **Temp files** | Debug scripts in `_test_scripts/` (not committed). |

## Frontend (React/TypeScript)

| Standard | Rule |
|---|---|
| **Components** | Functional + hooks only. TypeScript interfaces, never `any`. |
| **Organization** | Reusable: `components/common/`. Feature: `components/features/`. |
| **Styling** | Module CSS or styled-components. Mobile-first responsive. |

## General

| Standard | Rule |
|---|---|
| **API** | RESTful. JSON bodies/responses. |
| **Git** | Present tense commits. Feature branches → Main. Never commit secrets. |
| **Paths** | Use `Path(__file__).parent` — never hardcoded CWD paths. |

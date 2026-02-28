# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Commento is a Korean hate speech detection and comment moderation API. It serves as the backend for a Chrome Extension that intercepts YouTube comments, analyzes them using a two-stage pipeline (local ML classification + LLM rewriting), and provides feedback or corrections for problematic content.

## Tech Stack

- **Python 3.13** (strictly `==3.13.*`)
- **FastAPI** web framework with Uvicorn ASGI server
- **PDM** for dependency management (not pip/poetry)
- **HuggingFace Transformers** + PyTorch for hate speech classification (`beomi/korean-hatespeech-multilabel`, KcELECTRA-base)
- **OpenAI GPT-4o-mini** for comment rewriting and feedback generation (async calls via `openai` SDK)
- **Docker** multi-stage build for deployment

## Development Commands

```bash
# Install dependencies (creates .venv)
pdm install

# Run dev server with auto-reload
pdm run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Docker build & run
docker build -t commento .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... commento
```

No test suite exists yet. API docs at `http://localhost:8000/docs`.

On first run, the HuggingFace model (~400MB) downloads automatically to `~/.cache/huggingface/`.

## Architecture

### Two-Stage Pipeline

1. **Fast local classifier** (`src/app/models/classifier.py`): Singleton `HateSpeechClassifier` loaded once at import time. Runs synchronous CPU-bound inference via HuggingFace `pipeline("text-classification", top_k=None)`. Labels: `hate`, `offensive`, `bias_gender`, `bias_others`.
2. **LLM API call** (`src/app/utils/llm.py`): Only triggered when content is classified as problematic. Async OpenAI calls for rewriting or explanation.

### API Endpoints (all rate-limited to 100/min)

| Endpoint | Flow | Purpose |
|---|---|---|
| `POST /api/review` | Classify only | Returns `{is_problematic: bool}` |
| `POST /api/correct` | Classify → LLM rewrite if problematic | Returns `{corrected_comment: str}` |
| `POST /api/feedback` | Classify → LLM explanation if problematic | Returns severity, problem types, reason, etc. |

### Key Source Files

- `src/main.py` — FastAPI app + all route definitions
- `src/config.py` — Environment-aware config (`ENV=development|production`)
- `src/app/services/comment_service.py` — Core business logic orchestrating classify → LLM calls
- `src/app/models/classifier.py` — Singleton ML model wrapper
- `src/app/utils/llm.py` — Async OpenAI API calls (reads `OPENAI_API_KEY` from env directly)
- `src/app/utils/constants.py` — Label mappings and threshold constants
- `src/app/schemas/comment.py` — Pydantic request/response DTOs

### Design Patterns

- **Singleton classifier**: Model is expensive to load, instantiated once at module import, reused across all requests
- **Async/sync split**: `classify()` is synchronous (CPU-bound); `correct()` and `get_feedback()` are async (I/O-bound LLM calls)
- **Stateless**: No database or persistence layer
- **No auth**: API endpoints have no authentication

## Configuration

Environment variable `ENV` selects config (`development` default, `production` uses GPU with `DEVICE=0`). Required env var: `OPENAI_API_KEY`. The `.env` file is loaded via python-dotenv.

## Language

All user-facing strings (API responses, LLM prompts, severity labels) are in Korean.

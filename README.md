# AI Resume Analyzer

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/resumeai/main.py`](src/resumeai/main.py) | HTTP handlers: `GET /healthz`, `POST /match` |
| [`src/resumeai/match.py`](src/resumeai/match.py) | Functions: `tokens`, `match` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/resumeai/__init__.py`](src/resumeai/__init__.py) | Implementation or supporting configuration |
| [`tests/test_match.py`](tests/test_match.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn resumeai.main:app --reload
```

<!-- project-guide:end -->

Level: 5 — NLP & Generative AI

Skills: Python, overlap against a role profile

Score a resume against two role blurbs. No hosted model is called.

```bash
pip install -r requirements.txt
pytest -q
```

This is a local laptop proof. It does not call a hosted model and it does not apply production changes.

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.

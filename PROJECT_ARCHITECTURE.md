# ai-resume-analyzer — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Score a resume against two role blurbs. No hosted model is called.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/resumeai/__init__.py"]
    M1["src/resumeai/main.py"]
    M2["src/resumeai/match.py"]
    M3["src/resumeai/ops.py"]
    M1 -->|imports| M2
    M1 -->|imports| M3
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/resumeai/main.py`](src/resumeai/main.py) | HTTP handlers: `GET /healthz`, `POST /match` |
| [`src/resumeai/ops.py`](src/resumeai/ops.py) | HTTP handlers: `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}` |
| [`src/resumeai/match.py`](src/resumeai/match.py) | Functions: `tokens`, `match` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/resumeai/__init__.py`](src/resumeai/__init__.py) | Implementation or supporting configuration |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`Makefile`](Makefile) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`tests/test_match.py`](tests/test_match.py) | Executable checks and regression examples |
| [`tests/test_ops.py`](tests/test_ops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Project explanations or operating notes |

## Existing design and operating guides

These checked-in guides provide the project’s detailed design, operational context, or deployment view:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/resumeai/main.py`](src/resumeai/main.py#L10) |
| `POST /match` | `post_match` | [`src/resumeai/main.py`](src/resumeai/main.py#L15) |
| `GET /readyz` | `readyz` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L74) |
| `POST /workspaces` | `create_workspace` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L80) |
| `GET /workspaces` | `list_workspaces` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L98) |
| `POST /workspaces/{workspace_id}/jobs` | `create_job` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L106) |
| `GET /jobs/{job_id}` | `get_job` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L130) |
| `POST /jobs/{job_id}/approve` | `approve_job` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L140) |
| `GET /audit` | `audit` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L160) |
| `GET /metrics` | `metrics` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L176) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `match(resume)`

Source: [`src/resumeai/match.py`](src/resumeai/match.py#L10).

Calls visible in this function: `JOBS.items`, `ValueError`, `isinstance`, `len`, `ranked.append`, `ranked.sort`, `resume.strip`, `round`, `tokens`.

```python
def match(resume):
    if not isinstance(resume, str) or not resume.strip():
        raise ValueError("resume is empty")
    left = tokens(resume)
    ranked = []
    for name, text in JOBS.items():
        right = tokens(text)
        score = len(left & right) / len(left | right) if left | right else 0
        ranked.append({"job": name, "score": round(score, 4)})
    ranked.sort(key=lambda row: -row["score"])
    return {"matches": ranked}
```

### `tokens(text)`

Source: [`src/resumeai/match.py`](src/resumeai/match.py#L6).

Calls visible in this function: `re.findall`, `set`, `text.lower`.

```python
def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/resumeai/main.py`](src/resumeai/main.py#L19) |
| `ValueError('resume is empty')` | [`src/resumeai/match.py`](src/resumeai/match.py#L12) |
| `HTTPException(status_code=404, detail='workspace not found')` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L77) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L100) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L109) |
| `HTTPException(status_code=403, detail='production apply is disabled in this lab')` | [`src/resumeai/ops.py`](src/resumeai/ops.py#L113) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/resumeai/match.py`](src/resumeai/match.py) defines module-level containers: `JOBS`.
- [`src/resumeai/ops.py`](src/resumeai/ops.py) defines module-level containers: `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `match`

In [`src/resumeai/match.py`](src/resumeai/match.py#L10), `match(resume)` receives the inputs. The function computes these intermediate values:

- `left = tokens(resume)`
- `ranked = []`

Its result is defined by:

- `{'matches': ranked}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/resumeai/match.py`](src/resumeai/match.py#L10) branches on:

- `not isinstance(resume, str) or not resume.strip()`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

### What does the operations plane add, and where is its limit

[`src/resumeai/ops.py`](src/resumeai/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_match.py`](tests/test_match.py), [`tests/test_ops.py`](tests/test_ops.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.

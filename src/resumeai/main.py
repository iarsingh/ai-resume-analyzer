from fastapi import FastAPI, HTTPException
from resumeai.match import match

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/match")
def post_match(body: dict):
    try:
        return match(body.get("resume"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

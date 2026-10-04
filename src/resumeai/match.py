import re

JOBS = {"fde": 'customer constraint metric kubernetes terraform python', "ml": 'sklearn training drift registry serving'}


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


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

from fastapi.testclient import TestClient
from resumeai.main import app

client = TestClient(app)


def test_ranks_the_closest_job():
    payload = client.post("/match", json={"resume": 'customer kubernetes terraform metric python'}).json()
    assert payload["matches"][0]["job"] == "fde"

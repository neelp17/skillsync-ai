from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from routes import analyses as analyses_route

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_database_session():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_database_session
client = TestClient(app)
analyses_route.analyze_skills = lambda skills, role: {"analysis": f"Roadmap for {role}: {skills}", "source": "fallback"}
OWNER = "c2d91348-0e4a-4a50-8f1b-49ab5f44c819"
OTHER = "a0fc80a0-56dc-4125-8336-c4723742b6af"


def test_analysis_crud_is_scoped_to_owner():
    headers = {"X-User-Id": OWNER}
    response = client.post("/analyses", headers=headers, json={"role": "Backend Developer", "skills": "Python"})
    assert response.status_code == 201
    record = response.json()
    record_id = record["id"]

    listed = client.get("/analyses", headers=headers)
    assert [item["id"] for item in listed.json()] == [record_id]
    assert client.get(f"/analyses/{record_id}", headers={"X-User-Id": OTHER}).status_code == 404

    updated = client.patch(f"/analyses/{record_id}", headers=headers, json={"role": "DevOps Engineer"})
    assert updated.status_code == 200
    assert updated.json()["role"] == "DevOps Engineer"
    assert "DevOps Engineer" in updated.json()["analysis"]

    assert client.delete(f"/analyses/{record_id}", headers=headers).status_code == 204
    assert client.get(f"/analyses/{record_id}", headers=headers).status_code == 404

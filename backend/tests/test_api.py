import uuid
import pytest
from fastapi.testclient import TestClient
from main import app, seed_database
@pytest.fixture(autouse=True)
def run_seed():
    seed_database()

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"

def test_login_demo_admin():
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            data={"username": "admin@campuseventpro.edu", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"

def test_login_demo_student():
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            data={"username": "student@campuseventpro.edu", "password": "student123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "student"

def test_get_events():
    with TestClient(app) as client:
        response = client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        assert len(events) > 0

def test_get_calendar_events():
    with TestClient(app) as client:
        response = client.get("/api/calendar/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)

def test_event_registration_api():
    with TestClient(app) as client:
        # Fetch an event first
        events_resp = client.get("/api/events")
        events = events_resp.json()
        target_event_id = events[0]["id"]
        initial_seats = events[0]["seats_taken"]

        unique_id = uuid.uuid4().hex[:6].upper()
        payload = {
            "eventId": target_event_id,
            "fullName": "Alex Johnson",
            "rollNumber": f"TEST2026-{unique_id}",
            "email": f"alex.{unique_id}@campuseventpro.edu",
            "phone": "9876543210"
        }

        # 1. Register Student
        res = client.post("/api/registrations", json=payload)
        assert res.status_code == 201
        res_data = res.json()
        assert res_data["success"] is True
        assert res_data["message"] == "Registration Successful"

        # 2. Test Duplicate Registration Prevention
        dup_res = client.post("/api/registrations", json=payload)
        assert dup_res.status_code == 201 or dup_res.status_code == 200 or dup_res.status_code == 400
        dup_data = dup_res.json()
        assert dup_data["success"] is False
        assert dup_data["message"] == "You have already registered."

        # 3. Verify Seat Occupancy Incremented
        event_check = client.get(f"/api/events/{target_event_id}").json()
        assert event_check["seats_taken"] == initial_seats + 1

def test_admin_registration_disabled():
    with TestClient(app) as client:
        res = client.post("/api/auth/register", json={
            "full_name": "Fake Admin",
            "email": "hacker.admin@campuseventpro.edu",
            "password": "password123",
            "role": "admin",
            "department": "Administration"
        })
        assert res.status_code == 400
        assert "Admin registration is disabled" in res.json()["detail"]

def test_teacher_coordinator_flow():
    with TestClient(app) as client:
        uid = uuid.uuid4().hex[:6].upper()
        email = f"prof.{uid.lower()}@campuseventpro.edu"
        emp_id = f"EMP-{uid}"

        # 1. Register Teacher Coordinator
        reg_res = client.post("/api/auth/register-teacher", json={
            "name": f"Prof. {uid}",
            "employee_id": emp_id,
            "email": email,
            "phone": "9876543210",
            "department": "Computer Science",
            "password": "teacherpassword123",
            "confirm_password": "teacherpassword123"
        })
        assert reg_res.status_code == 201
        assert reg_res.json()["status"] == "pending"

        # 2. Login as pending teacher (must be blocked)
        login_pending = client.post("/api/auth/login", data={"username": email, "password": "teacherpassword123"})
        assert login_pending.status_code == 403

        # 3. Login as Admin
        admin_login = client.post("/api/auth/login", data={"username": "admin@campuseventpro.edu", "password": "admin123"})
        admin_token = admin_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 4. Get list of teachers and approve the new teacher
        teachers_list = client.get("/api/admin/teachers", headers=headers).json()
        new_teacher = next(t for t in teachers_list if t["email"] == email)
        
        approve_res = client.put(f"/api/admin/teachers/{new_teacher['id']}/status", json={"status": "approved"}, headers=headers)
        assert approve_res.status_code == 200

        # 5. Login as approved teacher (must succeed)
        login_approved = client.post("/api/auth/login", data={"username": email, "password": "teacherpassword123"})
        assert login_approved.status_code == 200
        assert login_approved.json()["user"]["role"] == "teacher_coordinator"

        # 6. Assign teacher to event #1
        assign_res = client.put(f"/api/admin/events/1/assign-coordinator", json={"coordinator_id": new_teacher['id']}, headers=headers)
        assert assign_res.status_code == 200

        # 7. Check event #1 displays coordinator details
        ev = client.get("/api/events/1").json()
        assert ev["coordinator_id"] == new_teacher['id']
        assert ev["coordinator_name"] == f"Prof. {uid}"


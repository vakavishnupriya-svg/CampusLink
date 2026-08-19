import os
import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models import User, Event, EventRegistration, Bookmark, Notification, Certificate, Attendance, TeacherCoordinator
from backend.security import hash_password
from backend.routes import auth, users, events, calendar, notifications, attendance, certificates, admin, registrations

from sqlalchemy import inspect, text

# Create tables and run column migrations if not exist
with engine.connect() as conn:
    inspector = inspect(engine)
    if "events" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("events")]
        if "coordinator_id" not in columns:
            conn.execute(text("ALTER TABLE events ADD COLUMN coordinator_id INTEGER REFERENCES teacher_coordinators(id)"))
            conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Full-Stack Event Management System with Internal Calendar",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if "*" in origins or not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file directories setup
static_dir = os.path.join(os.path.dirname(__file__), "static")
qrcodes_dir = os.path.join(static_dir, "qrcodes")
certs_dir = os.path.join(static_dir, "certificates")

os.makedirs(qrcodes_dir, exist_ok=True)
os.makedirs(certs_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount API Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(calendar.router)
app.include_router(notifications.router)
app.include_router(attendance.router)
app.include_router(certificates.router)
app.include_router(admin.router)
app.include_router(registrations.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.ENV,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# Seed database on startup
def seed_database():
    db = SessionLocal()
    try:
        teacher_count = db.query(TeacherCoordinator).count()
        if teacher_count == 0:
            print("[SEED] Seeding Teacher Coordinators...")
            approved_teacher = TeacherCoordinator(
                name="Prof. Sarah Jenkins",
                employee_id="EMP-101",
                email="teacher@campuseventpro.edu",
                phone="9876543210",
                department="Computer Science",
                password_hash=hash_password("teacher123"),
                status="approved"
            )
            pending_teacher = TeacherCoordinator(
                name="Dr. Robert Lang",
                employee_id="EMP-102",
                email="robert.lang@campuseventpro.edu",
                phone="9876543211",
                department="Information Technology",
                password_hash=hash_password("teacher123"),
                status="pending"
            )
            db.add_all([approved_teacher, pending_teacher])
            db.commit()

        user_count = db.query(User).count()
        if user_count == 0:
            print("[SEED] Initializing Database Seed Data...")
            
            admin_user = User(
                full_name="Dr. Arthur Pendelton",
                email="admin@campuseventpro.edu",
                hashed_password=hash_password("admin123"),
                role="admin",
                department="Administration",
                roll_number="ADM-001",
                bio="Chief Administrator & Campus Event Director",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop"
            )
            
            faculty_user = User(
                full_name="Prof. Sarah Jenkins",
                email="faculty@campuseventpro.edu",
                hashed_password=hash_password("faculty123"),
                role="faculty",
                department="Computer Science",
                roll_number="FAC-102",
                bio="Senior Associate Professor of AI & Robotics",
                avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop"
            )
            
            student_user = User(
                full_name="Alex Rivera",
                email="student@campuseventpro.edu",
                hashed_password=hash_password("student123"),
                role="student",
                department="Computer Science",
                roll_number="CSEIOT23045",
                bio="3rd Year Computer Science Undergrad | Tech Lead at Coding Club",
                avatar_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop"
            )

            db.add_all([admin_user, faculty_user, student_user])
            db.commit()
            db.refresh(faculty_user)
            db.refresh(student_user)

            now = datetime.datetime.utcnow()
            teacher_co = db.query(TeacherCoordinator).filter(TeacherCoordinator.email == "teacher@campuseventpro.edu").first()
            coord_id = teacher_co.id if teacher_co else None

            sample_events = [
                Event(
                    title="InnovateAI 2026 Hackathon & Symposium",
                    description="Join 500+ student developers for an intense 36-hour hackathon focused on Generative AI, Autonomous Robotics, and Sustainable Tech. Cash prizes up to $10,000!",
                    category="Hackathon",
                    department="Computer Science",
                    organizer_id=faculty_user.id,
                    venue="Main Auditorium & Innovation Lab 3",
                    start_time=now + datetime.timedelta(days=2, hours=4),
                    end_time=now + datetime.timedelta(days=3, hours=16),
                    capacity=250,
                    seats_taken=184,
                    registration_deadline=now + datetime.timedelta(days=1),
                    banner_url="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=True,
                    is_paid=False,
                    speaker_name="Dr. Marcus Vance",
                    speaker_title="VP of AI Research at OpenAI",
                    coordinator_id=coord_id
                ),
                Event(
                    title="Annual Spring Cultural Fest - Rhythm & Harmony",
                    description="The largest cultural festival of the year! Live battle of the bands, classical dance showcases, theatrical performances, and street food stalls.",
                    category="Cultural",
                    department="Cultural Club",
                    organizer_id=admin_user.id,
                    venue="Open Air Amphitheatre",
                    start_time=now + datetime.timedelta(days=5, hours=2),
                    end_time=now + datetime.timedelta(days=6, hours=10),
                    capacity=1000,
                    seats_taken=620,
                    registration_deadline=now + datetime.timedelta(days=4),
                    banner_url="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=True,
                    is_paid=False,
                    speaker_name="Elena Rostova",
                    speaker_title="Grammy Award Winning Violinist"
                ),
                Event(
                    title="Global Tech Career Fair & Placement Drive 2026",
                    description="Meet recruiters from over 60 Fortune 500 tech companies and high-growth startups. On-spot interview rooms, resume review booths, and networking lounges.",
                    category="Placement",
                    department="Placement Cell",
                    organizer_id=faculty_user.id,
                    venue="University Student Center - Level 2",
                    start_time=now + datetime.timedelta(days=8, hours=1),
                    end_time=now + datetime.timedelta(days=8, hours=8),
                    capacity=500,
                    seats_taken=340,
                    registration_deadline=now + datetime.timedelta(days=7),
                    banner_url="https://images.unsplash.com/photo-1511578314322-379afb476865?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=False,
                    is_paid=False,
                    speaker_name="David Sterling",
                    speaker_title="Head of Global Talent Acquisition"
                ),
                Event(
                    title="Inter-Departmental Athletics & Football Tournament",
                    description="Cheer for your department! Men's and Women's football league, sprint track, high jump, and table tennis championship.",
                    category="Sports",
                    department="Physical Education",
                    organizer_id=admin_user.id,
                    venue="Central Sports Complex Field A",
                    start_time=now + datetime.timedelta(days=12, hours=3),
                    end_time=now + datetime.timedelta(days=14, hours=6),
                    capacity=300,
                    seats_taken=190,
                    registration_deadline=now + datetime.timedelta(days=10),
                    banner_url="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=False,
                    is_paid=False,
                    speaker_name="Coach Ryan Miller",
                    speaker_title="National Athletics Coach"
                ),
                Event(
                    title="Hands-on Workshop: Full-Stack Web Dev with Fast-API & Cloud",
                    description="Master modern backend microservices, async databases, Docker containerization, and serverless deployment workflows.",
                    category="Workshop",
                    department="Information Technology",
                    organizer_id=faculty_user.id,
                    venue="Computer Center - Lab 4",
                    start_time=now + datetime.timedelta(days=1, hours=2),
                    end_time=now + datetime.timedelta(days=1, hours=6),
                    capacity=60,
                    seats_taken=45,
                    registration_deadline=now + datetime.timedelta(hours=12),
                    banner_url="https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=True,
                    is_paid=False,
                    speaker_name="Prof. Sarah Jenkins",
                    speaker_title="Senior Faculty IT"
                ),
                Event(
                    title="Guest Seminar: Quantum Computing & The Next Frontier",
                    description="An insightful lecture into quantum cryptography, qubit architectures, and supercomputing applications in financial modeling and drug discovery.",
                    category="Seminar",
                    department="Physics & Mathematics",
                    organizer_id=admin_user.id,
                    venue="Science Hall Seminar Room B",
                    start_time=now + datetime.timedelta(days=18, hours=5),
                    end_time=now + datetime.timedelta(days=18, hours=7),
                    capacity=120,
                    seats_taken=78,
                    registration_deadline=now + datetime.timedelta(days=16),
                    banner_url="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1000&auto=format&fit=crop",
                    status="approved",
                    is_featured=False,
                    is_paid=False,
                    speaker_name="Dr. Aris Thorne",
                    speaker_title="Quantum Fellow at MIT"
                )
            ]
            db.add_all(sample_events)
            db.commit()
            print("[SUCCESS] Database Seeded Successfully with Default Users and College Events!")

    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    seed_database()

# Mount Frontend Static Web Application under Root / AT THE VERY END
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

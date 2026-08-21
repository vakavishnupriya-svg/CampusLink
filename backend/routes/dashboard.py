import datetime
from typing import Optional, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, TeacherCoordinator, Event, EventRegistration
from auth import get_optional_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: Optional[Any] = Depends(get_optional_user)):
    now = datetime.datetime.utcnow()

    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(TeacherCoordinator).count()
    total_events = db.query(Event).count()
    total_registrations = db.query(EventRegistration).count()
    upcoming_events_count = db.query(Event).filter(Event.start_time >= now).count()

    recent_regs = db.query(EventRegistration).order_by(EventRegistration.registered_at.desc()).limit(6).all()
    recent_registrations = [
        {
            "id": r.id,
            "registration_id": r.registration_id or f"REG-{r.id}",
            "full_name": r.full_name,
            "roll_no": r.roll_no,
            "email": r.email,
            "phone": r.phone or "N/A",
            "event_name": r.event_name or (r.event.title if r.event else f"Event #{r.event_id}"),
            "registered_at": r.registered_at.isoformat() if r.registered_at else None
        }
        for r in recent_regs
    ]

    dept_counts = db.query(Event.department, func.count(Event.id)).group_by(Event.department).all()
    department_stats = [{"department": d[0], "count": d[1]} for d in dept_counts]

    monthly_counts = [0] * 12
    all_regs = db.query(EventRegistration.registered_at).all()
    for r in all_regs:
        if r[0]:
            month_idx = r[0].month - 1
            if 0 <= month_idx < 12:
                monthly_counts[month_idx] += 1

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_registrations = [{"month": month_names[i], "count": monthly_counts[i]} for i in range(12)]

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_events": total_events,
        "total_registrations": total_registrations,
        "upcoming_events": upcoming_events_count,
        "recent_registrations": recent_registrations,
        "department_stats": department_stats,
        "monthly_registrations": monthly_registrations
    }

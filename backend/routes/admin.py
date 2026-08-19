import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from backend.database import get_db
from backend.models import User, Event, EventRegistration, Certificate, Attendance, TeacherCoordinator
from backend.schemas import AnalyticsResponse, UserResponse, RegistrationResponse, TeacherCoordinatorResponse, TeacherStatusUpdate, EventAssignCoordinator
from backend.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# --- Teacher Coordinator Management Endpoints ---
@router.get("/teachers", response_model=List[TeacherCoordinatorResponse])
def get_all_teachers_admin(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    teachers = db.query(TeacherCoordinator).order_by(TeacherCoordinator.created_at.desc()).all()
    results = []
    for t in teachers:
        assigned_title = None
        if t.assigned_event_id:
            ev = db.query(Event).filter(Event.id == t.assigned_event_id).first()
            if ev:
                assigned_title = ev.title
        results.append(TeacherCoordinatorResponse(
            id=t.id,
            name=t.name,
            employee_id=t.employee_id,
            email=t.email,
            phone=t.phone,
            department=t.department,
            status=t.status,
            assigned_event_id=t.assigned_event_id,
            assigned_event_title=assigned_title,
            created_at=t.created_at
        ))
    return results

@router.put("/teachers/{teacher_id}/status")
def update_teacher_status(
    teacher_id: int,
    payload: TeacherStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher Coordinator not found")

    new_status = payload.status.lower().strip()
    if new_status not in ["approved", "pending", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be approved, pending, or rejected.")

    teacher.status = new_status
    db.commit()
    db.refresh(teacher)

    return {
        "success": True,
        "message": f"Teacher Coordinator account status updated to '{new_status.capitalize()}'.",
        "status": teacher.status
    }

@router.delete("/teachers/{teacher_id}")
def delete_teacher_coordinator(
    teacher_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher Coordinator not found")

    # Unassign from events
    events = db.query(Event).filter(Event.coordinator_id == teacher_id).all()
    for ev in events:
        ev.coordinator_id = None

    db.delete(teacher)
    db.commit()
    return {"success": True, "message": "Teacher Coordinator deleted successfully"}

@router.put("/events/{event_id}/assign-coordinator")
def assign_event_coordinator(
    event_id: int,
    payload: EventAssignCoordinator,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if payload.coordinator_id is not None:
        teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.id == payload.coordinator_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher Coordinator not found")
        if teacher.status != "approved":
            raise HTTPException(status_code=400, detail="Only approved Teacher Coordinators can be assigned to events.")

        # Update event and teacher links
        event.coordinator_id = teacher.id
        teacher.assigned_event_id = event.id
    else:
        # Unassign coordinator
        if event.coordinator_id:
            old_teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.id == event.coordinator_id).first()
            if old_teacher:
                old_teacher.assigned_event_id = None
        event.coordinator_id = None

    db.commit()
    db.refresh(event)

    coordinator_name = event.coordinator.name if event.coordinator else "Unassigned"
    return {
        "success": True,
        "message": f"Event coordinator updated to '{coordinator_name}'.",
        "event_id": event.id,
        "coordinator_id": event.coordinator_id
    }

@router.get("/analytics", response_model=AnalyticsResponse)
def get_admin_analytics(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_faculty = db.query(User).filter(User.role == "faculty").count()

    total_events = db.query(Event).count()
    active_events = db.query(Event).filter(Event.status == "approved").count()
    total_registrations = db.query(EventRegistration).count()
    total_certificates = db.query(Certificate).count()

    total_attendances = db.query(Attendance).count()
    attendance_rate = round((total_attendances / total_registrations * 100), 1) if total_registrations > 0 else 0.0

    events_per_month = [
        {"month": "Jan", "count": 12},
        {"month": "Feb", "count": 19},
        {"month": "Mar", "count": 15},
        {"month": "Apr", "count": 22},
        {"month": "May", "count": 28},
        {"month": "Jun", "count": 18},
        {"month": "Jul", "count": 24},
        {"month": "Aug", "count": 31}
    ]

    cat_counts = db.query(Event.category, func.count(Event.id)).group_by(Event.category).all()
    category_distribution = [{"category": c[0], "count": c[1]} for c in cat_counts]

    dept_counts = db.query(Event.department, func.count(Event.id)).group_by(Event.department).all()
    department_stats = [{"department": d[0], "events": d[1]} for d in dept_counts]

    return AnalyticsResponse(
        total_users=total_users,
        total_students=total_students,
        total_faculty=total_faculty,
        total_events=total_events,
        active_events=active_events,
        total_registrations=total_registrations,
        total_certificates=total_certificates,
        attendance_rate=attendance_rate,
        events_per_month=events_per_month,
        category_distribution=category_distribution,
        department_stats=department_stats
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users_admin(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.asc()).all()

@router.get("/registrations", response_model=List[RegistrationResponse])
def get_all_registrations_admin(
    search: Optional[str] = None,
    department: Optional[str] = None,
    event_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(EventRegistration)

    if search:
        sp = f"%{search}%"
        query = query.filter(
            or_(
                EventRegistration.roll_no.ilike(sp),
                EventRegistration.full_name.ilike(sp),
                EventRegistration.email.ilike(sp),
                EventRegistration.registration_id.ilike(sp)
            )
        )

    if department and department != "All":
        query = query.filter(EventRegistration.department == department)

    if event_id and event_id != 0:
        query = query.filter(EventRegistration.event_id == event_id)

    if status_filter and status_filter != "All":
        query = query.filter(EventRegistration.status == status_filter)

    regs = query.order_by(EventRegistration.registered_at.desc()).all()
    
    results = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        results.append(RegistrationResponse(
            id=r.id,
            registration_id=r.registration_id or f"REG-{r.id}",
            event_id=r.event_id,
            event_name=r.event_name or (ev.title if ev else "Campus Event"),
            full_name=r.full_name,
            roll_no=r.roll_no,
            email=r.email,
            phone=r.phone,
            department=r.department,
            year=r.year,
            section=r.section,
            status=r.status,
            attendance=r.attendance,
            registered_at=r.registered_at,
            qr_code_token=r.qr_code_token,
            qr_code_url=r.qr_code_url
        ))
    return results

@router.put("/registrations/{reg_id}/status")
def update_registration_status(
    reg_id: int,
    status_val: str = Query(..., alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if status_val not in ["approved", "pending", "rejected", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    reg = db.query(EventRegistration).filter(EventRegistration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration record not found")

    reg.status = status_val
    db.commit()
    return {"message": f"Registration status updated to {status_val}"}

@router.delete("/registrations/{reg_id}")
def delete_registration(
    reg_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    reg = db.query(EventRegistration).filter(EventRegistration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration record not found")

    ev = db.query(Event).filter(Event.id == reg.event_id).first()
    if ev and ev.seats_taken > 0:
        ev.seats_taken -= 1

    db.delete(reg)
    db.commit()
    return {"message": "Registration deleted"}

@router.get("/registrations/export")
def export_registrations_csv(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Reg ID", "Roll No", "Student Name", "Email", "Phone", "Department", "Year", "Section", "Event Name", "Status", "Attendance", "Registered At"])

    regs = db.query(EventRegistration).all()
    for r in regs:
        writer.writerow([
            r.registration_id or f"REG-{r.id}",
            r.roll_no,
            r.full_name,
            r.email,
            r.phone,
            r.department,
            r.year,
            r.section,
            r.event_name,
            r.status,
            "Present" if r.attendance == 1 else "Absent",
            r.registered_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=student_registrations_report.csv"
    return response

@router.get("/export")
def export_system_data(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["=== CAMPUS EVENT PRO SYSTEM REPORT ==="])
    writer.writerow([])
    writer.writerow(["USER SUMMARY"])
    writer.writerow(["ID", "Name", "Email", "Role", "Department", "Created At"])

    users = db.query(User).all()
    for u in users:
        writer.writerow([u.id, u.full_name, u.email, u.role, u.department, u.created_at])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=campus_event_pro_report.csv"
    return response

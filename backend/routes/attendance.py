import csv
import io
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Attendance, Event, User, EventRegistration, Certificate, Notification
from backend.schemas import AttendanceCheckinRequest, AttendanceResponse
from backend.auth import get_current_user, require_faculty_or_admin
from backend.utils.pdf_generator import generate_pdf_certificate

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("/checkin", response_model=AttendanceResponse)
def checkin_attendee(
    req: AttendanceCheckinRequest,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    ev = db.query(Event).filter(Event.id == req.event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    target_user_id = None
    
    if req.qr_token:
        reg = db.query(EventRegistration).filter(
            EventRegistration.qr_code_token == req.qr_token,
            EventRegistration.event_id == req.event_id
        ).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Invalid QR entry ticket for this event")
        target_user_id = reg.user_id
    elif req.user_id:
        target_user_id = req.user_id
    else:
        raise HTTPException(status_code=400, detail="Must provide either qr_token or user_id")

    # Check for existing attendance
    existing_att = db.query(Attendance).filter(
        Attendance.event_id == req.event_id,
        Attendance.user_id == target_user_id
    ).first()

    student = db.query(User).filter(User.id == target_user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    if existing_att:
        return AttendanceResponse(
            id=existing_att.id,
            event_id=ev.id,
            user_id=student.id,
            user_name=student.full_name,
            checked_in_at=existing_att.checked_in_at,
            method=existing_att.method
        )

    # Record attendance
    method_used = "qr" if req.qr_token else "manual"
    att = Attendance(
        event_id=ev.id,
        user_id=student.id,
        checked_in_at=datetime.datetime.utcnow(),
        method=method_used
    )
    db.add(att)

    # Update registration status
    reg_record = db.query(EventRegistration).filter(
        EventRegistration.event_id == ev.id,
        EventRegistration.user_id == student.id
    ).first()
    if reg_record:
        reg_record.status = "attended"

    # Automatically issue Certificate of Participation
    cert_no = f"CERT-{ev.id:04d}-{student.id:04d}"
    existing_cert = db.query(Certificate).filter(Certificate.certificate_number == cert_no).first()
    if not existing_cert:
        pdf_url = generate_pdf_certificate(
            student_name=student.full_name,
            event_title=ev.title,
            event_date=ev.start_time.strftime("%B %d, %Y"),
            organizer_name=ev.organizer.full_name if ev.organizer else "Campus Event Pro",
            certificate_number=cert_no
        )
        cert = Certificate(
            certificate_number=cert_no,
            user_id=student.id,
            event_id=ev.id,
            pdf_path=pdf_url,
            verification_url=f"/frontend/profile.html?cert={cert_no}"
        )
        db.add(cert)

        # Notify student about Certificate
        cert_notif = Notification(
            user_id=student.id,
            title="Certificate Earned!",
            message=f"Congratulations! Your Certificate of Participation for '{ev.title}' is now ready to download.",
            type="certificate",
            link="/frontend/profile.html"
        )
        db.add(cert_notif)

    db.commit()
    db.refresh(att)

    return AttendanceResponse(
        id=att.id,
        event_id=ev.id,
        user_id=student.id,
        user_name=student.full_name,
        checked_in_at=att.checked_in_at,
        method=att.method
    )


@router.get("/event/{event_id}", response_model=List[AttendanceResponse])
def get_event_attendance(
    event_id: int,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    records = db.query(Attendance).filter(Attendance.event_id == event_id).all()
    results = []
    for r in records:
        u = db.query(User).filter(User.id == r.user_id).first()
        results.append(AttendanceResponse(
            id=r.id,
            event_id=r.event_id,
            user_id=r.user_id,
            user_name=u.full_name if u else "Student",
            checked_in_at=r.checked_in_at,
            method=r.method
        ))
    return results


@router.get("/export/{event_id}")
def export_attendance_csv(
    event_id: int,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    records = db.query(Attendance).filter(Attendance.event_id == event_id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Attendance ID", "Student Name", "Email", "Department", "Roll Number", "Check-in Time", "Method"])

    for r in records:
        u = db.query(User).filter(User.id == r.user_id).first()
        writer.writerow([
            r.id,
            u.full_name if u else "Unknown",
            u.email if u else "N/A",
            u.department if u else "N/A",
            u.roll_number if u else "N/A",
            r.checked_in_at.strftime("%Y-%m-%d %H:%M:%S"),
            r.method
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=attendance_event_{event_id}.csv"
    return response

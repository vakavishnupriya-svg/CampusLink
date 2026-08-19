import uuid
import datetime
import io
import csv
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from backend.database import get_db
from backend.models import Event, EventRegistration, User
from backend.utils.qr_generator import generate_qr_code_file

router = APIRouter(prefix="/api/registrations", tags=["Registrations"])

class RegistrationPayload(BaseModel):
    eventId: int
    fullName: str = Field(..., min_length=3, max_length=50)
    rollNumber: str = Field(..., pattern=r"^\S+$")
    email: EmailStr
    phone: str = Field(..., pattern=r"^[0-9]{10}$")

@router.post("", status_code=201)
@router.post("/", status_code=201)
def create_registration(payload: RegistrationPayload, db: Session = Depends(get_db)):
    # 1. Check if event exists
    event = db.query(Event).filter(Event.id == payload.eventId).first()
    if not event:
        return {"success": False, "message": "Event not found."}

    # 2. Check for duplicate registration for this event and roll number
    existing = db.query(EventRegistration).filter(
        EventRegistration.event_id == payload.eventId,
        EventRegistration.roll_no == payload.rollNumber
    ).first()

    if existing:
        return {"success": False, "message": "You have already registered."}

    # 3. Create registration
    reg_uuid = f"REG-2026-{uuid.uuid4().hex[:6].upper()}"
    qr_token = f"CEP-{payload.eventId}-{uuid.uuid4().hex[:8].upper()}"
    qr_url = generate_qr_code_file(qr_token, reg_uuid)

    registration = EventRegistration(
        registration_id=reg_uuid,
        event_id=payload.eventId,
        event_name=event.title,
        full_name=payload.fullName.strip(),
        roll_no=payload.rollNumber.strip(),
        email=payload.email.strip(),
        phone=payload.phone.strip(),
        department=event.department,
        status="approved",
        qr_code_token=qr_token,
        qr_code_url=qr_url,
        registered_at=datetime.datetime.utcnow()
    )

    db.add(registration)

    # 4. Increment seat count
    event.seats_taken = (event.seats_taken or 0) + 1
    db.commit()
    db.refresh(registration)

    return {
        "success": True,
        "message": "Registration Successful",
        "data": {
            "id": registration.id,
            "registrationId": registration.registration_id,
            "eventId": registration.event_id,
            "eventName": registration.event_name,
            "fullName": registration.full_name,
            "rollNumber": registration.roll_no,
            "email": registration.email,
            "phone": registration.phone,
            "registeredAt": registration.registered_at.isoformat(),
            "qrCodeUrl": registration.qr_code_url
        }
    }


@router.get("")
@router.get("/")
def get_registrations(
    eventId: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 0,
    size: int = 10,
    sortBy: str = "registered_at",
    sortDir: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(EventRegistration)

    if eventId:
        query = query.filter(EventRegistration.event_id == eventId)

    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            (EventRegistration.full_name.ilike(s)) |
            (EventRegistration.roll_no.ilike(s)) |
            (EventRegistration.email.ilike(s)) |
            (EventRegistration.phone.ilike(s))
        )

    if sortDir.lower() == "asc":
        query = query.order_by(getattr(EventRegistration, sortBy, EventRegistration.registered_at).asc())
    else:
        query = query.order_by(getattr(EventRegistration, sortBy, EventRegistration.registered_at).desc())

    total_elements = query.count()
    items = query.offset(page * size).limit(size).all()

    content = []
    for reg in items:
        event_name = reg.event_name or (reg.event.title if reg.event else f"Event #{reg.event_id}")
        content.append({
            "id": reg.id,
            "registrationId": reg.registration_id,
            "eventId": reg.event_id,
            "eventTitle": event_name,
            "fullName": reg.full_name,
            "rollNumber": reg.roll_no,
            "email": reg.email,
            "phone": reg.phone or "",
            "department": reg.department or "General",
            "status": reg.status,
            "registeredAt": reg.registered_at.isoformat() if reg.registered_at else None
        })

    return {
        "success": True,
        "message": "Registrations retrieved successfully",
        "data": {
            "content": content,
            "totalElements": total_elements,
            "totalPages": (total_elements + size - 1) // size if size > 0 else 1,
            "page": page,
            "size": size
        }
    }


@router.get("/export")
def export_registrations(
    eventId: Optional[int] = None,
    search: Optional[str] = None,
    format: str = "csv",
    db: Session = Depends(get_db)
):
    query = db.query(EventRegistration)
    if eventId:
        query = query.filter(EventRegistration.event_id == eventId)
    if search and search.strip():
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            (EventRegistration.full_name.ilike(s)) |
            (EventRegistration.roll_no.ilike(s)) |
            (EventRegistration.email.ilike(s))
        )
    regs = query.order_by(EventRegistration.registered_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Event ID", "Event Name", "Full Name", "Roll Number", "Email", "Phone", "Registered At"])

    for r in regs:
        event_name = r.event_name or (r.event.title if r.event else f"Event #{r.event_id}")
        writer.writerow([
            r.id,
            r.event_id,
            event_name,
            r.full_name,
            r.roll_no,
            r.email,
            r.phone or "",
            r.registered_at.strftime("%Y-%m-%d %H:%M:%S") if r.registered_at else ""
        ])

    output.seek(0)
    filename = f"event_registrations_2026.{'xlsx' if format in ['excel', 'xlsx'] else 'csv'}"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{id}")
def get_registration_by_id(id: int, db: Session = Depends(get_db)):
    reg = db.query(EventRegistration).filter(EventRegistration.id == id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    event_name = reg.event_name or (reg.event.title if reg.event else f"Event #{reg.event_id}")
    return {
        "success": True,
        "message": "Registration details",
        "data": {
            "id": reg.id,
            "registrationId": reg.registration_id,
            "eventId": reg.event_id,
            "eventTitle": event_name,
            "fullName": reg.full_name,
            "rollNumber": reg.roll_no,
            "email": reg.email,
            "phone": reg.phone or "",
            "department": reg.department or "General",
            "status": reg.status,
            "registeredAt": reg.registered_at.isoformat() if reg.registered_at else None
        }
    }


@router.delete("/{id}")
def delete_registration(id: int, db: Session = Depends(get_db)):
    reg = db.query(EventRegistration).filter(EventRegistration.id == id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Decrement seats_taken on event
    if reg.event and reg.event.seats_taken > 0:
        reg.event.seats_taken -= 1

    db.delete(reg)
    db.commit()

    return {
        "success": True,
        "message": "Registration deleted successfully"
    }

import datetime
import uuid
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from database import get_db
from models import Event, User, EventRegistration, Bookmark, Notification, Certificate, Attendance
from schemas import EventCreate, EventResponse, EventUpdate, RegistrationResponse, EventRegistrationRequest
from auth import get_current_user, get_optional_user, require_faculty_or_admin
from utils.qr_generator import generate_qr_code_file, generate_qr_code_base64
from utils.pdf_generator import generate_pdf_certificate

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[EventResponse])
def get_events(
    search: Optional[str] = None,
    category: Optional[str] = None,
    department: Optional[str] = None,
    status_filter: Optional[str] = "approved",
    is_featured: Optional[bool] = None,
    sort_by: Optional[str] = "newest",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    query = db.query(Event)

    if status_filter and status_filter != "all":
        query = query.filter(Event.status == status_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Event.title.ilike(search_pattern),
                Event.description.ilike(search_pattern),
                Event.venue.ilike(search_pattern),
                Event.speaker_name.ilike(search_pattern)
            )
        )

    if category and category != "All":
        query = query.filter(Event.category == category)

    if department and department != "All":
        query = query.filter(Event.department == department)

    if is_featured is not None:
        query = query.filter(Event.is_featured == is_featured)

    # Sorting
    if sort_by == "popular":
        query = query.order_by(Event.seats_taken.desc())
    elif sort_by == "closest":
        query = query.filter(Event.start_time >= datetime.datetime.utcnow()).order_by(Event.start_time.asc())
    else:  # newest
        query = query.order_by(Event.created_at.desc())

    events = query.all()
    
    user_regs = set()
    user_bookmarks = set()
    if current_user:
        regs = db.query(EventRegistration.event_id).filter(
            EventRegistration.user_id == current_user.id,
            EventRegistration.status != "cancelled"
        ).all()
        user_regs = {r[0] for r in regs}

        bms = db.query(Bookmark.event_id).filter(Bookmark.user_id == current_user.id).all()
        user_bookmarks = {b[0] for b in bms}

    results = []
    for ev in events:
        organizer_name = ev.organizer.full_name if ev.organizer else "Campus Event Pro Admin"
        coord_id = ev.coordinator_id
        coord_name = ev.coordinator.name if ev.coordinator else None
        coord_dept = ev.coordinator.department if ev.coordinator else None

        ev_resp = EventResponse(
            id=ev.id,
            title=ev.title,
            description=ev.description,
            category=ev.category,
            department=ev.department,
            organizer_id=ev.organizer_id,
            organizer_name=organizer_name,
            coordinator_id=coord_id,
            coordinator_name=coord_name,
            coordinator_department=coord_dept,
            venue=ev.venue,
            start_time=ev.start_time,
            end_time=ev.end_time,
            capacity=ev.capacity,
            seats_taken=ev.seats_taken,
            registration_deadline=ev.registration_deadline,
            banner_url=ev.banner_url,
            status=ev.status,
            is_featured=ev.is_featured,
            is_paid=ev.is_paid,
            ticket_price=ev.ticket_price,
            speaker_name=ev.speaker_name,
            speaker_title=ev.speaker_title,
            created_at=ev.created_at,
            is_user_registered=(ev.id in user_regs),
            is_user_bookmarked=(ev.id in user_bookmarks)
        )
        results.append(ev_resp)

    return results


@router.get("/{event_id}", response_model=EventResponse)
def get_event_by_id(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    is_registered = False
    is_bookmarked = False
    if current_user:
        reg = db.query(EventRegistration).filter(
            EventRegistration.event_id == ev.id,
            EventRegistration.user_id == getattr(current_user, "id", None),
            EventRegistration.status != "cancelled"
        ).first()
        is_registered = bool(reg)

        bm = db.query(Bookmark).filter(
            Bookmark.event_id == ev.id,
            Bookmark.user_id == getattr(current_user, "id", None)
        ).first()
        is_bookmarked = bool(bm)

    organizer_name = ev.organizer.full_name if ev.organizer else "Campus Event Pro Admin"
    coord_id = ev.coordinator_id
    coord_name = ev.coordinator.name if ev.coordinator else None
    coord_dept = ev.coordinator.department if ev.coordinator else None

    return EventResponse(
        id=ev.id,
        title=ev.title,
        description=ev.description,
        category=ev.category,
        department=ev.department,
        organizer_id=ev.organizer_id,
        organizer_name=organizer_name,
        coordinator_id=coord_id,
        coordinator_name=coord_name,
        coordinator_department=coord_dept,
        venue=ev.venue,
        start_time=ev.start_time,
        end_time=ev.end_time,
        capacity=ev.capacity,
        seats_taken=ev.seats_taken,
        registration_deadline=ev.registration_deadline,
        banner_url=ev.banner_url,
        status=ev.status,
        is_featured=ev.is_featured,
        is_paid=ev.is_paid,
        ticket_price=ev.ticket_price,
        speaker_name=ev.speaker_name,
        speaker_title=ev.speaker_title,
        created_at=ev.created_at,
        is_user_registered=is_registered,
        is_user_bookmarked=is_bookmarked
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    new_event = Event(
        title=event_in.title,
        description=event_in.description,
        category=event_in.category,
        department=event_in.department,
        organizer_id=current_user.id,
        venue=event_in.venue,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        capacity=event_in.capacity,
        seats_taken=0,
        registration_deadline=event_in.registration_deadline,
        banner_url=event_in.banner_url or "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1000&auto=format&fit=crop",
        status="approved",
        is_featured=event_in.is_featured,
        is_paid=event_in.is_paid,
        ticket_price=event_in.ticket_price,
        speaker_name=event_in.speaker_name,
        speaker_title=event_in.speaker_title
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    all_users = db.query(User).all()
    for u in all_users:
        notif = Notification(
            user_id=u.id,
            title=f"New Event Published: {new_event.title}",
            message=f"{new_event.department} published '{new_event.title}'. Registration is now open!",
            type="event",
            link=f"event-details.html?id={new_event.id}"
        )
        db.add(notif)
    db.commit()

    return EventResponse(
        id=new_event.id,
        title=new_event.title,
        description=new_event.description,
        category=new_event.category,
        department=new_event.department,
        organizer_id=new_event.organizer_id,
        organizer_name=current_user.full_name,
        venue=new_event.venue,
        start_time=new_event.start_time,
        end_time=new_event.end_time,
        capacity=new_event.capacity,
        seats_taken=new_event.seats_taken,
        registration_deadline=new_event.registration_deadline,
        banner_url=new_event.banner_url,
        status=new_event.status,
        is_featured=new_event.is_featured,
        is_paid=new_event.is_paid,
        ticket_price=new_event.ticket_price,
        speaker_name=new_event.speaker_name,
        speaker_title=new_event.speaker_title,
        created_at=new_event.created_at,
        is_user_registered=False,
        is_user_bookmarked=False
    )


@router.post("/{event_id}/register", response_model=RegistrationResponse)
def register_for_event(
    event_id: int,
    reg_req: Optional[EventRegistrationRequest] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    if ev.seats_taken >= ev.capacity:
        raise HTTPException(status_code=400, detail="Event is full")

    full_name = reg_req.full_name if reg_req else (current_user.full_name if current_user else "Student")
    roll_no = reg_req.roll_no if reg_req else (current_user.roll_number if current_user else "CSEIOT23045")
    email = reg_req.email if reg_req else (current_user.email if current_user else "student@campuseventpro.edu")
    raw_phone = reg_req.phone if reg_req else "9876543210"
    department = reg_req.department if reg_req else (current_user.department if current_user else ev.department)
    year = reg_req.year if reg_req else "3rd Year"
    section = reg_req.section if reg_req else "Sec A"

    # Clean & Validate 10-digit Indian Mobile Number
    clean_digits = re.sub(r'\D', '', str(raw_phone))
    if len(clean_digits) == 12 and clean_digits.startswith("91"):
        clean_digits = clean_digits[2:]
        
    if len(clean_digits) != 10:
        raise HTTPException(status_code=400, detail="Phone number must contain exactly 10 digits")

    formatted_phone = f"+91 {clean_digits}"

    # Prevent duplicate registration for the same event
    dup_query = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.status != "cancelled",
        or_(
            EventRegistration.roll_no == roll_no,
            EventRegistration.email == email,
            EventRegistration.user_id == (current_user.id if current_user else -1)
        )
    ).first()

    if dup_query:
        raise HTTPException(status_code=400, detail="You have already registered for this event")

    reg_id = f"REG-2026-{uuid.uuid4().hex[:6].upper()}"
    qr_token = f"CEP-{uuid.uuid4().hex[:12].upper()}"
    qr_payload = f"EVENT:{ev.id}|REG:{reg_id}|TOKEN:{qr_token}"
    qr_url = generate_qr_code_file(qr_payload, f"ticket_{qr_token}")

    new_reg = EventRegistration(
        registration_id=reg_id,
        user_id=current_user.id if current_user else None,
        event_id=ev.id,
        event_name=ev.title,
        full_name=full_name,
        roll_no=roll_no,
        email=email,
        phone=formatted_phone,
        department=department,
        year=year,
        section=section,
        status="approved",
        attendance=0,
        qr_code_token=qr_token,
        qr_code_url=qr_url
    )
    
    ev.seats_taken += 1
    db.add(new_reg)

    if current_user:
        notif = Notification(
            user_id=current_user.id,
            title=f"Registration Confirmed: {ev.title}",
            message=f"Registered for {ev.title}. Reg ID: {reg_id}. Phone: {formatted_phone}",
            type="event",
            link=f"event-details.html?id={ev.id}"
        )
        db.add(notif)

    db.commit()
    db.refresh(new_reg)

    return RegistrationResponse(
        id=new_reg.id,
        registration_id=new_reg.registration_id,
        event_id=ev.id,
        event_name=ev.title,
        full_name=new_reg.full_name,
        roll_no=new_reg.roll_no,
        email=new_reg.email,
        phone=new_reg.phone,
        department=new_reg.department,
        year=new_reg.year,
        section=new_reg.section,
        status=new_reg.status,
        attendance=new_reg.attendance,
        registered_at=new_reg.registered_at,
        qr_code_token=new_reg.qr_code_token,
        qr_code_url=new_reg.qr_code_url
    )


@router.post("/{event_id}/unregister")
def unregister_from_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reg = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.id,
        EventRegistration.status != "cancelled"
    ).first()

    if not reg:
        raise HTTPException(status_code=404, detail="Active registration not found")

    reg.status = "cancelled"
    ev = db.query(Event).filter(Event.id == event_id).first()
    if ev and ev.seats_taken > 0:
        ev.seats_taken -= 1

    db.commit()
    return {"message": "Successfully unregistered from event"}


@router.post("/{event_id}/bookmark")
def toggle_bookmark(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bm = db.query(Bookmark).filter(
        Bookmark.event_id == event_id,
        Bookmark.user_id == current_user.id
    ).first()

    if bm:
        db.delete(bm)
        db.commit()
        return {"bookmarked": False, "message": "Bookmark removed"}
    else:
        new_bm = Bookmark(user_id=current_user.id, event_id=event_id)
        db.add(new_bm)
        db.commit()
        return {"bookmarked": True, "message": "Event bookmarked"}


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(ev, field, value)

    db.commit()
    db.refresh(ev)

    organizer_name = ev.organizer.full_name if ev.organizer else "Campus Event Pro Admin"
    coord_name = ev.coordinator.name if ev.coordinator else None
    coord_dept = ev.coordinator.department if ev.coordinator else None

    return EventResponse(
        id=ev.id,
        title=ev.title,
        description=ev.description,
        category=ev.category,
        department=ev.department,
        organizer_id=ev.organizer_id,
        organizer_name=organizer_name,
        coordinator_id=ev.coordinator_id,
        coordinator_name=coord_name,
        coordinator_department=coord_dept,
        venue=ev.venue,
        start_time=ev.start_time,
        end_time=ev.end_time,
        capacity=ev.capacity,
        seats_taken=ev.seats_taken,
        registration_deadline=ev.registration_deadline,
        banner_url=ev.banner_url,
        status=ev.status,
        is_featured=ev.is_featured,
        is_paid=ev.is_paid,
        ticket_price=ev.ticket_price,
        speaker_name=ev.speaker_name,
        speaker_title=ev.speaker_title,
        created_at=ev.created_at
    )


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(ev)
    db.commit()
    return {"success": True, "message": "Event deleted successfully"}

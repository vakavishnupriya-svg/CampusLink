import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Event
from backend.schemas import EventResponse
from backend.auth import get_optional_user, User

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

@router.get("/events", response_model=List[EventResponse])
def get_calendar_events(
    start_date: Optional[str] = None,  # YYYY-MM-DD
    end_date: Optional[str] = None,    # YYYY-MM-DD
    department: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    query = db.query(Event).filter(Event.status == "approved")

    if start_date:
        try:
            st = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Event.start_time >= st)
        except ValueError:
            pass

    if end_date:
        try:
            et = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)
            query = query.filter(Event.end_time <= et)
        except ValueError:
            pass

    if department and department != "All":
        query = query.filter(Event.department == department)

    if category and category != "All":
        query = query.filter(Event.category == category)

    events = query.all()

    results = []
    for ev in events:
        results.append(EventResponse(
            id=ev.id,
            title=ev.title,
            description=ev.description,
            category=ev.category,
            department=ev.department,
            organizer_id=ev.organizer_id,
            organizer_name=ev.organizer.full_name if ev.organizer else "Admin",
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
        ))
    return results

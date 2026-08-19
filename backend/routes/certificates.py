from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from backend.database import get_db
from backend.models import Certificate, User, Event
from backend.schemas import CertificateResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

@router.get("", response_model=List[CertificateResponse])
def get_user_certificates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).all()
    results = []
    for c in certs:
        ev = db.query(Event).filter(Event.id == c.event_id).first()
        results.append(CertificateResponse(
            id=c.id,
            certificate_number=c.certificate_number,
            user_id=c.user_id,
            user_name=current_user.full_name,
            event_id=c.event_id,
            event_title=ev.title if ev else "Campus Event",
            issued_at=c.issued_at,
            download_url=c.pdf_path
        ))
    return results

@router.get("/{cert_id}", response_model=CertificateResponse)
def get_certificate_by_id(cert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Certificate not found")

    ev = db.query(Event).filter(Event.id == c.event_id).first()
    u = db.query(User).filter(User.id == c.user_id).first()

    return CertificateResponse(
        id=c.id,
        certificate_number=c.certificate_number,
        user_id=c.user_id,
        user_name=u.full_name if u else "Student",
        event_id=c.event_id,
        event_title=ev.title if ev else "Campus Event",
        issued_at=c.issued_at,
        download_url=c.pdf_path
    )

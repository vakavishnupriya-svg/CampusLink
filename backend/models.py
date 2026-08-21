import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)  # 'student', 'faculty', 'admin'
    department = Column(String(100), default="Computer Science")
    roll_number = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    events_organized = relationship("Event", back_populates="organizer")
    registrations = relationship("EventRegistration", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    attendances = relationship("Attendance", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    department = Column(String(100), nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    venue = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=100)
    seats_taken = Column(Integer, default=0)
    registration_deadline = Column(DateTime, nullable=False)
    banner_url = Column(String(500), nullable=True)
    status = Column(String(20), default="approved")  # 'pending', 'approved', 'rejected', 'completed'
    is_featured = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    ticket_price = Column(Float, default=0.0)
    speaker_name = Column(String(100), nullable=True)
    speaker_title = Column(String(100), nullable=True)
    coordinator_id = Column(Integer, ForeignKey("teacher_coordinators.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organizer = relationship("User", back_populates="events_organized")
    coordinator = relationship("TeacherCoordinator", foreign_keys=[coordinator_id], back_populates="events_coordinated")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="event", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="event", cascade="all, delete-orphan")


class TeacherCoordinator(Base):
    __tablename__ = "teacher_coordinators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    department = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # 'pending', 'approved', 'rejected'
    assigned_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    events_coordinated = relationship("Event", foreign_keys=[Event.coordinator_id], back_populates="coordinator")
    assigned_event = relationship("Event", foreign_keys=[assigned_event_id])


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(String(100), unique=True, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    event_name = Column(String(200), nullable=True)
    full_name = Column(String(100), nullable=False)
    roll_no = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    year = Column(String(20), default="3rd Year")
    section = Column(String(20), default="Sec A")
    status = Column(String(20), default="approved")  # 'approved', 'pending', 'rejected', 'cancelled'
    attendance = Column(Integer, default=0)  # 0: Not Checked in, 1: Present
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    qr_code_token = Column(String(100), unique=True, nullable=False)
    qr_code_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    event = relationship("Event", back_populates="bookmarks")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checked_in_at = Column(DateTime, default=datetime.datetime.utcnow)
    method = Column(String(20), default="qr")

    event = relationship("Event", back_populates="attendances")
    user = relationship("User", back_populates="attendances")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(100), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
    pdf_path = Column(String(500), nullable=False)
    verification_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="certificates")
    event = relationship("Event", back_populates="certificates")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")

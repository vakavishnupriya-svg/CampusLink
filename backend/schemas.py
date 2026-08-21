import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# User Schemas
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "student"
    department: str = "Computer Science"
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserPasswordReset(BaseModel):
    email: EmailStr

class UserPasswordConfirm(BaseModel):
    token: str
    new_password: str

class UserResponse(UserBase):
    id: int
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# Teacher Coordinator Schemas
class TeacherRegisterRequest(BaseModel):
    name: str
    employee_id: str
    email: EmailStr
    phone: str
    department: str
    password: str
    confirm_password: Optional[str] = None

class TeacherCoordinatorResponse(BaseModel):
    id: int
    name: str
    employee_id: str
    email: str
    phone: str
    department: str
    status: str
    assigned_event_id: Optional[int] = None
    assigned_event_title: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TeacherStatusUpdate(BaseModel):
    status: str  # 'approved' or 'rejected'

class EventAssignCoordinator(BaseModel):
    coordinator_id: Optional[int] = None

# Event Schemas
class EventBase(BaseModel):
    title: str
    description: str
    category: str
    department: str
    venue: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    capacity: int = 100
    registration_deadline: datetime.datetime
    banner_url: Optional[str] = None
    is_featured: bool = False
    is_paid: bool = False
    ticket_price: float = 0.0
    speaker_name: Optional[str] = None
    speaker_title: Optional[str] = None
    coordinator_id: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    venue: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    capacity: Optional[int] = None
    registration_deadline: Optional[datetime.datetime] = None
    banner_url: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_paid: Optional[bool] = None
    ticket_price: Optional[float] = None
    speaker_name: Optional[str] = None
    speaker_title: Optional[str] = None
    coordinator_id: Optional[int] = None

class EventResponse(EventBase):
    id: int
    organizer_id: int
    organizer_name: Optional[str] = None
    coordinator_id: Optional[int] = None
    coordinator_name: Optional[str] = None
    coordinator_department: Optional[str] = None
    seats_taken: int
    status: str
    created_at: datetime.datetime
    is_user_registered: Optional[bool] = False
    is_user_bookmarked: Optional[bool] = False

    class Config:
        from_attributes = True

# Student Event Registration Form Payload
class EventRegistrationRequest(BaseModel):
    full_name: str
    roll_no: str
    email: EmailStr
    phone: str
    department: str
    year: str = "3rd Year"
    section: str = "Sec A"

class RegistrationResponse(BaseModel):
    id: int
    registration_id: str
    event_id: int
    event_name: str
    full_name: str
    roll_no: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    section: Optional[str] = None
    status: str
    attendance: int
    registered_at: datetime.datetime
    qr_code_token: str
    qr_code_url: Optional[str] = None

    class Config:
        from_attributes = True

# Attendance Schema
class AttendanceCheckinRequest(BaseModel):
    qr_token: Optional[str] = None
    user_id: Optional[int] = None
    event_id: int

class AttendanceResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str
    checked_in_at: datetime.datetime
    method: str

# Certificate Schema
class CertificateResponse(BaseModel):
    id: int
    certificate_number: str
    user_id: int
    user_name: str
    event_id: int
    event_title: str
    issued_at: datetime.datetime
    download_url: str

# Notification Schema
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Admin Schemas
class AnalyticsResponse(BaseModel):
    total_users: int
    total_students: int
    total_faculty: int
    total_events: int
    active_events: int
    total_registrations: int
    total_certificates: int
    attendance_rate: float
    events_per_month: List[dict]
    category_distribution: List[dict]
    department_stats: List[dict]

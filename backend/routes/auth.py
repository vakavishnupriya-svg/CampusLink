import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User, Notification, TeacherCoordinator
from schemas import UserCreate, UserResponse, Token, UserPasswordReset, UserPasswordConfirm, TeacherRegisterRequest
from security import hash_password, verify_password
from utils.jwt_handler import create_access_token
from utils.email_service import send_password_reset_email
from auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.role.lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin registration is disabled. Admin accounts must be created manually in the database."
        )

    email = user_in.email.lower().strip()
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    roll_no = user_in.roll_number.strip() if user_in.roll_number else None
    if roll_no:
        existing_roll = db.query(User).filter(User.roll_number == roll_no).first()
        if existing_roll:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this Roll Number already exists"
            )

    clean_phone = user_in.phone.strip() if user_in.phone else None
    if clean_phone:
        import re
        digits_only = re.sub(r'\D', '', clean_phone)
        if len(digits_only) == 12 and digits_only.startswith("91"):
            digits_only = digits_only[2:]
        if len(digits_only) == 10:
            clean_phone = f"+91 {digits_only}"

    hashed_pw = hash_password(user_in.password)
    user = User(
        full_name=user_in.full_name.strip(),
        email=email,
        hashed_password=hashed_pw,
        role=user_in.role.lower() if user_in.role.lower() in ["student", "faculty"] else "student",
        department=user_in.department,
        roll_number=roll_no,
        phone=clean_phone,
        bio=user_in.bio
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    welcome_notif = Notification(
        user_id=user.id,
        title="Welcome to Campus Event Pro!",
        message="Your account has been created successfully. Explore upcoming campus events and internal calendar.",
        type="event"
    )
    db.add(welcome_notif)
    db.commit()

    token_data = {"sub": user.email, "role": user.role}
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register-teacher", status_code=status.HTTP_201_CREATED)
def register_teacher(teacher_in: TeacherRegisterRequest, db: Session = Depends(get_db)):
    if teacher_in.confirm_password and teacher_in.password != teacher_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and Confirm Password do not match."
        )

    # Check duplicate email
    email = teacher_in.email.lower().strip()
    if db.query(User).filter(User.email == email).first() or db.query(TeacherCoordinator).filter(TeacherCoordinator.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Check duplicate employee_id
    emp_id = teacher_in.employee_id.strip()
    if db.query(TeacherCoordinator).filter(TeacherCoordinator.employee_id == emp_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A Teacher Coordinator with this Employee ID already exists."
        )

    teacher = TeacherCoordinator(
        name=teacher_in.name.strip(),
        employee_id=emp_id,
        email=email,
        phone=teacher_in.phone.strip(),
        department=teacher_in.department.strip(),
        password_hash=hash_password(teacher_in.password),
        status="pending"
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {
        "success": True,
        "message": "Registration submitted successfully! Your account is pending Admin approval.",
        "status": "pending",
        "teacher_id": teacher.id
    }

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated. Please contact administrator."
            )

        token_data = {"sub": user.email, "role": user.role}
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    # Check TeacherCoordinator table
    teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.email == email).first()
    if teacher:
        if not verify_password(form_data.password, teacher.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if teacher.status.lower() != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your Teacher Coordinator account status is '{teacher.status.capitalize()}'. Please wait for Admin approval before logging in."
            )

        token_data = {"sub": teacher.email, "role": "teacher_coordinator"}
        access_token = create_access_token(data=token_data)

        user_dict = {
            "id": teacher.id,
            "full_name": teacher.name,
            "email": teacher.email,
            "role": "teacher_coordinator",
            "department": teacher.department,
            "roll_number": teacher.employee_id,
            "phone": teacher.phone,
            "avatar_url": None,
            "is_active": True,
            "created_at": teacher.created_at
        }

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
def forgot_password(payload: UserPasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        reset_token = str(uuid.uuid4())
        send_password_reset_email(user.email, reset_token)
    return {"message": "If an account with that email exists, a password reset link has been dispatched."}

@router.post("/reset-password")
def reset_password(payload: UserPasswordConfirm, db: Session = Depends(get_db)):
    # Simple token validation demo simulation
    if not payload.token or len(payload.token) < 5:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"message": "Password successfully updated. You may now log in with your new password."}

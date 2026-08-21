from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User, TeacherCoordinator
from utils.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
        
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        return user

    teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.email == email).first()
    if teacher is not None:
        if teacher.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your Teacher Coordinator account is pending admin approval."
            )
        # Create user-like object wrapper
        teacher.full_name = teacher.name
        teacher.role = "teacher_coordinator"
        teacher.roll_number = teacher.employee_id
        return teacher
        
    raise credentials_exception

def get_optional_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Any]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        email = payload.get("sub")
        if not email:
            return None
        user = db.query(User).filter(User.email == email).first()
        if user:
            return user
        teacher = db.query(TeacherCoordinator).filter(TeacherCoordinator.email == email).first()
        if teacher and teacher.status == "approved":
            teacher.full_name = teacher.name
            teacher.role = "teacher_coordinator"
            teacher.roll_number = teacher.employee_id
            return teacher
        return None
    except Exception:
        return None

def require_admin(current_user: Any = Depends(get_current_user)) -> Any:
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_teacher_or_admin(current_user: Any = Depends(get_current_user)) -> Any:
    role = getattr(current_user, "role", None)
    if role not in ["teacher_coordinator", "teacher", "faculty", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher Coordinator or Admin privileges required"
        )
    return current_user

def require_faculty_or_admin(current_user: Any = Depends(get_current_user)) -> Any:
    role = getattr(current_user, "role", None)
    if role not in ["faculty", "admin", "teacher_coordinator", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty or Admin privileges required"
        )
    return current_user

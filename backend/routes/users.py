from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from auth import get_current_user, require_admin

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.department is not None:
        current_user.department = user_update.department
    if user_update.roll_number is not None:
        current_user.roll_number = user_update.roll_number
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=list[UserResponse])
def get_all_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).all()

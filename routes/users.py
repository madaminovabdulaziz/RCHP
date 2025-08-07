# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from datetime import datetime
#
# from models import ModelUser, ModelNationality
# from schemas.users import UserCreate, UserResponse, UserUpdate
# from database import get_db
#
# user_router = APIRouter(tags=["Users"])
#
#
# # CREATE walk-in user
# @user_router.post("/users/walk-in", response_model=UserResponse)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     is_nationality = db.query(ModelNationality).filter(ModelNationality.id == user.nationality).first()
#     if not is_nationality:
#         raise HTTPException(status_code=400, detail="Nationality does not exist!")
#
#     new_user = ModelUser(
#         name=user.name,
#         phone=user.phone,
#         email=user.email,
#         nationality_id=user.nationality,
#         created_at=datetime.now(),
#         status="walk_in"  # default status
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user
#
#
# # GET all walk-in users
# @user_router.get("/users/get-walk-in", response_model=list[UserResponse])
# def get_walkin_users(db: Session = Depends(get_db)):
#     users = db.query(ModelUser).filter(ModelUser.status == "walk_in").all()
#     return users
#
#
# @user_router.get("/users/get-cofirmed", response_model=list[UserResponse])
# def get_walkin_users(db: Session = Depends(get_db)):
#     users = db.query(ModelUser).filter(ModelUser.status == "confirmed").all()
#     return users
#
#
# # GET single user by ID
# @user_router.get("/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
#
#
# # UPDATE user info
# @user_router.put("/users/{user_id}/status", response_model=UserResponse)
# def update_user_status(user_id: int, status: str, db: Session = Depends(get_db)):
#     is_user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
#     if is_user:
#         db.query(ModelUser).filter(ModelUser.id == user_id).update({
#             ModelUser.status: status
#         })
#         db.commit()
#
#     else:
#         raise HTTPException(status_code=404, detail="No such user!")
#
#
# # DELETE user
# @user_router.delete("/users/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db.delete(user)
#     db.commit()
#     return {"detail": f"User {user_id} deleted"}

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import re
import logging
from typing import List, Optional
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from models import ModelUser, ModelNationality
from schemas.users import UserCreate, UserResponse, BookedCreate, BookedResponse
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)
user_router = APIRouter(tags=["Users"])

# Phone number regex (basic validation, adjust as needed)
PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    return bool(re.match(PHONE_REGEX, phone))


# CREATE walk-in user
@user_router.post("/users/walk-in", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new walk-in user."""
    try:
        if not validate_phone(user.phone):
            raise HTTPException(status_code=400, detail="Invalid phone number format")

        is_nationality = db.query(ModelNationality).filter(ModelNationality.id == user.nationality).first()
        if not is_nationality:
            raise HTTPException(status_code=400, detail="Nationality does not exist")

        new_user = ModelUser(
            name=user.name.strip(),
            phone=user.phone,
            email=user.email.lower() if user.email else None,
            nationality_id=user.nationality,
            created_at=datetime.now(),
            status="walk_in"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Created user: {new_user.name} (ID: {new_user.id})")
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating user: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# CREATE booked user
@user_router.post("/users/booked", response_model=UserResponse)
def create_booked_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new booked user."""
    try:
        if not validate_phone(user.phone):
            raise HTTPException(status_code=400, detail="Invalid phone number format")

        is_nationality = db.query(ModelNationality).filter(ModelNationality.id == user.nationality).first()
        if not is_nationality:
            raise HTTPException(status_code=400, detail="Nationality does not exist")

        new_user = ModelUser(
            name=user.name.strip(),
            phone=user.phone,
            email=user.email.lower() if user.email else None,
            nationality_id=user.nationality,
            created_at=datetime.now(),
            status="confirmed"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Created user: {new_user.name} (ID: {new_user.id})")
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating user: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@user_router.get("/users")
def get_users(
        db: Session = Depends(get_db),
        status: Optional[str] = Query(None, enum=["walk_in", "confirmed", "booked", "rejected"]),
        search: Optional[str] = Query(None, min_length=1),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Get users with optional status filter, search, and pagination."""
    try:
        query = db.query(ModelUser).options(joinedload(ModelUser.nationality))
        if status:
            query = query.filter(ModelUser.status == status)
        if search:
            search = search.lower()
            query = query.filter(
                (ModelUser.name.ilike(f"%{search}%")) |
                (ModelUser.phone.ilike(f"%{search}%")) |
                (ModelUser.email.ilike(f"%{search}%")) |
                (ModelUser.created_at.ilike(f"%{search}%"))
            )
        users = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(users)} users with skip={skip}, limit={limit}, status={status}, search={search}")
        return users
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# GET single user by ID
@user_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    try:
        user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Retrieved user: {user.name} (ID: {user.id})")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# UPDATE user status
@user_router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: int, status: str = Query(..., enum=["walk_in", "confirmed", "booked", "rejected"]),
                       db: Session = Depends(get_db)):
    """Update user status."""
    try:
        user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.status = status
        db.commit()
        db.refresh(user)
        logger.info(f"Updated status for user {user_id} to {status}")
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# DELETE user
@user_router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID."""
    try:
        user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        logger.info(f"Deleted user: {user.name} (ID: {user_id})")
        return {"detail": f"User {user_id} deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# EXPORT users for PMS
@user_router.get("/users/export")
def export_users(db: Session = Depends(get_db),
                 status: Optional[str] = Query(None, enum=["walk_in", "confirmed", "booked"])):
    """Export users as CSV for PMS integration."""
    try:
        query = db.query(ModelUser)
        if status:
            query = query.filter(ModelUser.status == status)
        users = query.all()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Name", "Phone", "Email", "Nationality ID", "Status", "Created At"])
        for user in users:
            writer.writerow(
                [user.id, user.name, user.phone, user.email, user.nationality_id, user.status, user.created_at])

        output.seek(0)
        logger.info(f"Exported {len(users)} users as CSV")
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while exporting users: {e}")
        raise HTTPException(status_code=500, detail="Database error")

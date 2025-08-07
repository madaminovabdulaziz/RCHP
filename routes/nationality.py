from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from pydantic import BaseModel, Field

from models import ModelNationality, ModelUser
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)
nationality_router = APIRouter(tags=["Nationalities"])


class NationalityCreate(BaseModel):
    nationality: str = Field(..., min_length=1, max_length=255)


class NationalityResponse(BaseModel):
    id: int
    nationality: str

    class Config:
        orm_mode = True


# CREATE nationality
@nationality_router.post("/nationalities", response_model=NationalityResponse)
def create_nationality(nationality: NationalityCreate, db: Session = Depends(get_db)):
    """Create a new nationality."""
    try:
        existing_nationality = db.query(ModelNationality).filter(
            ModelNationality.nationality == nationality.nationality).first()
        if existing_nationality:
            raise HTTPException(status_code=400, detail="Nationality already exists")

        new_nationality = ModelNationality(nationality=nationality.nationality.strip())
        db.add(new_nationality)
        db.commit()
        db.refresh(new_nationality)
        logger.info(f"Created nationality: {new_nationality.nationality} (ID: {new_nationality.id})")
        return new_nationality
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating nationality: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# GET all nationalities
@nationality_router.get("/nationalities", response_model=list[NationalityResponse])
def get_all_nationalities(db: Session = Depends(get_db)):
    """Get all nationalities."""
    try:
        nationalities = db.query(ModelNationality).all()
        logger.info(f"Retrieved {len(nationalities)} nationalities")
        return nationalities
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving nationalities: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# UPDATE nationality
@nationality_router.put("/nationalities/{nationality_id}", response_model=NationalityResponse)
def update_nationality(nationality_id: int, nationality: NationalityCreate, db: Session = Depends(get_db)):
    """Update a nationality by ID."""
    try:
        existing_nationality = db.query(ModelNationality).filter(ModelNationality.id == nationality_id).first()
        if not existing_nationality:
            raise HTTPException(status_code=404, detail="Nationality not found")

        existing_nationality.nationality = nationality.nationality.strip()
        db.commit()
        db.refresh(existing_nationality)
        logger.info(f"Updated nationality: {existing_nationality.nationality} (ID: {nationality_id})")
        return existing_nationality
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating nationality {nationality_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# DELETE nationality
@nationality_router.delete("/nationalities/{nationality_id}")
def delete_nationality(nationality_id: int, db: Session = Depends(get_db)):
    """Delete a nationality by ID."""
    try:
        nationality = db.query(ModelNationality).filter(ModelNationality.id == nationality_id).first()
        if not nationality:
            raise HTTPException(status_code=404, detail="Nationality not found")

        if db.query(ModelUser).filter(ModelUser.nationality_id == nationality_id).first():
            raise HTTPException(status_code=400, detail="Cannot delete nationality with associated users")

        db.delete(nationality)
        db.commit()
        logger.info(f"Deleted nationality: {nationality.nationality} (ID: {nationality_id})")
        return {"detail": f"Nationality {nationality_id} deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting nationality {nationality_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from models import ModelCategories
from schemas.menu_categories import MenuCategories

client_menu_router = APIRouter(tags=["Client Menu"])


@client_menu_router.post('/menu/add', response_model=MenuCategories)
def post_categories(category: str, db: Session = Depends(get_db)):
    is_category = db.query(ModelCategories).filter(ModelCategories.category_name == category).first()
    if is_category:
        raise HTTPException(status_code=401, detail="This category already exists!")

    new_category = ModelCategories(
        category_name=category
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@client_menu_router.get("/menu/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(ModelCategories).all()

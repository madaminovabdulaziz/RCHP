from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from database import Base, engine
from sqlalchemy.orm import relationship


class ModelUser(Base):
    __tablename__ = 'users'
    name = Column(String(255))
    phone = Column(String(255), unique=True, primary_key=True)
    email = Column(String(255), unique=True)
    nationality_id = Column(Integer, ForeignKey('nationality.id'), nullable=False)
    nationality = relationship("ModelNationality", back_populates="users")
    created_at = Column(TIMESTAMP)
    status = Column(String(255))


class ModelAdmin(Base):
    __tablename__ = 'admins'
    login = Column(String(255), unique=True, primary_key=True)
    password = Column(String(255))


class ModelNationality(Base):
    __tablename__ = 'nationality'
    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    nationality = Column(String(255), unique=True)
    users = relationship("ModelUser", back_populates="nationality")


class ModelCategories(Base):
    __tablename__= 'menu_categories'
    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    category_name = Column(String(255), unique=True)

from pydantic import BaseModel, Field, computed_field
from datetime import datetime

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    nationality: int


class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    nationality_id: Optional[int]
    status: Optional[str]


class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[EmailStr]
    nationality_id: int
    created_at: datetime
    status: str
    
    class Config:
        orm_mode = True
        from_attributes = True


class UserBase(BaseModel):
    name: str = Field(..., example="John Doe")
    phone: str = Field(..., example="+998901234567")
    email: str = Field(..., example="bek@yahoo.com")
    nationality: int = Field(..., example=1)


class BookedUserBase(BaseModel):
    phone: str = Field(..., example='+998901234567')
    email: str = Field(..., example="bek@yahoo.com")
    nationality: int = Field(..., example=1)


class BookedCreate(BookedUserBase):
    pass


class BookedResponse(BookedUserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

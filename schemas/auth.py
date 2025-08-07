from pydantic import BaseModel


class AdminCreate(BaseModel):
    login: str
    password: str


class AdminResponse(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    admin: AdminResponse

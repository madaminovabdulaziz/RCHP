from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import ModelAdmin
from schemas.auth import TokenResponse, AdminResponse, AdminCreate

auth = APIRouter(tags=["Auth"])

# Config
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
SECRET_KEY = "99d6352a4f885394e82173981284336537df3dd564684557c523f1d49d40c774"
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_admin(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = db.query(ModelAdmin).filter(ModelAdmin.login == username).first()
    if not admin:
        raise credentials_exception
    return admin


# ========================
#     AUTH ROUTES
# ========================

@auth.post("/token", response_model=TokenResponse)
async def login_admin(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    admin = db.query(ModelAdmin).filter(ModelAdmin.login == form_data.username).first()

    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.login}, expires_delta=token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "username": admin.login
        }
    }


@auth.get("/admins/me", response_model=AdminResponse)
async def get_logged_admin(current_admin: ModelAdmin = Depends(get_current_admin)):
    return {
        "username": current_admin.login
    }


@auth.post("/admins", response_model=AdminResponse)
async def create_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_admin = db.query(ModelAdmin).filter(ModelAdmin.login == admin_data.login).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with this username already exists")

    hashed_password = get_password_hash(admin_data.password)

    new_admin = ModelAdmin(
        login=admin_data.login,
        password=hashed_password
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"username": new_admin.login}


@auth.get('/users/get-all-admins')
async def getAllAdmins(db: Session = Depends(get_db)):
    return db.query(ModelAdmin).all()

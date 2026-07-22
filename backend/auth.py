from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel, EmailStr

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from jose import JWTError, jwt

from database import get_db

from models import User

import os
from dotenv import load_dotenv


load_dotenv()



router = APIRouter()



# -------------------------
# Security Configuration
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise Exception(
        "SECRET_KEY missing from .env"
    )


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 60



pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)




# -------------------------
# Request Schemas
# -------------------------

class RegisterRequest(BaseModel):

    name: str

    email: EmailStr

    password: str




class LoginRequest(BaseModel):

    email: EmailStr

    password: str




class TokenResponse(BaseModel):

    access_token: str

    token_type: str




# -------------------------
# Password Functions
# -------------------------

def hash_password(password: str):

    return pwd_context.hash(password)




def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )




# -------------------------
# JWT Functions
# -------------------------

def create_access_token(data: dict):

    to_encode = data.copy()


    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )


    to_encode.update(
        {
            "exp": expire
        }
    )


    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )




# -------------------------
# Register User
# -------------------------

@router.post(
    "/register"
)
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):


    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()



    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )



    new_user = User(

        name=user.name,

        email=user.email,

        hashed_password=hash_password(
            user.password
        )
    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)



    return {

        "message": "Account created successfully",

        "user_id": new_user.id

    }




# -------------------------
# Login User
# -------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(

    user: LoginRequest,

    db: Session = Depends(get_db)

):


    db_user = db.query(User).filter(
        User.email == user.email
    ).first()



    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )



    if not verify_password(
        user.password,
        db_user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )



    token = create_access_token(
        {
            "sub": str(db_user.id)
        }
    )



    return {

        "access_token": token,

        "token_type": "bearer"

    }




# -------------------------
# Get Current User
# -------------------------

def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):


    credentials_exception = HTTPException(

        status_code=status.HTTP_401_UNAUTHORIZED,

        detail="Could not validate credentials",

        headers={
            "WWW-Authenticate": "Bearer"
        }

    )



    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[
                ALGORITHM
            ]

        )


        user_id = payload.get(
            "sub"
        )


        if user_id is None:

            raise credentials_exception



    except JWTError:

        raise credentials_exception



    user = db.query(User).filter(

        User.id == int(user_id)

    ).first()



    if user is None:

        raise credentials_exception



    return user
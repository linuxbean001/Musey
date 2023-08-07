from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from Object_Recognition.database import SessionLocal, engine
from sqlalchemy.orm import Session
import Object_Recognition.crud as crud
from utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

from jose import jwt
from pydantic import ValidationError

from Object_Recognition.schemas import User
import Object_Recognition.models as models

# reuseable_oauth = OAuth2PasswordBearer(
#     tokenUrl="/login",
#     scheme_name="JWT"
# )
oauth2_scheme = OAuth2PasswordBearer("login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        print("test")
        print(payload)
        user: Union[dict[str, Any], None] = crud.get_user_by_email(
            db, email=payload['sub'])

        print(user)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User.from_orm(user)

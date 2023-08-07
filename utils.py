from passlib.context import CryptContext
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from Object_Recognition.crud import get_user, get_user_by_email,create_moodboard_images_objects,insertcurrentdate
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
from sqlalchemy.orm import Session
from Object_Recognition.database import SessionLocal, engine
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'secmecode'   # should be kept secret
JWT_REFRESH_SECRET_KEY = 'secmecoderefresh'
API_DETECTION_ENDPOINT = "https://api.edenai.run/v2/image/object_detection"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDIzYTViNWEtMTdlNS00M2I4LWIzMjctMDE3M2ZiM2ZlN2U0IiwidHlwZSI6ImFwaV90b2tlbiJ9.H6IFysG8eeh86zQrl7IFVxokA2mpu1D7AX2eE0yPs1s"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    try:
        return password_context.hash(password)
        
    except:
        return "Hashed password not generated"


async def email_verify(db, token: str):
    try:
        payload = jwt.decode(token, "mtoken")
        user = get_user(db, payload["id"])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def userinfoforpass(db, token: str):

    try:
        payload = jwt.decode(token, 'rptoken')
        
        user = get_user_by_email(db, payload["emailuser"])
        print(user)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

async def userinfo(db, token: str):

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        user = get_user_by_email(db, payload["sub"])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def password_verification(password: str, hashed_pass: str):
    try:
        return password_context.verify(password, hashed_pass)
    except:
        return '{"verficationError":"Password not verified"}'


def create_token(subject: Union[str, Any], expires_time: int = None) -> str:
    if expires_time is not None:
        expires_time = datetime.utcnow() + expires_time
    else:
        expires_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_time, "sub": str(subject)}
    encoded_token = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_token


def create_refresh_token(subject: Union[str, Any], expires_time: int = None) -> str:
    if expires_time is not None:
        expires_time = datetime.utcnow() + expires_time
    else:
        expires_time = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_time, "sub": str(subject)}
    encoded_token = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_token

async def detectionimagesobjects(db, imageurl,imageid,moodid,userid):
    isimagegetlabels = False 
    moodimageobjects = [] 
    try:  
        urlimage = imageurl
        imageid = imageid
        # API endpoint for object detection
        endpoint = API_DETECTION_ENDPOINT
        # Request headers
        headers = {
            "Authorization": "Bearer "+API_KEY  # Replace with your Eden AI API key
        }
        print("static/moodimages/"+urlimage)
        files = {'file': open("static/moodimages/"+urlimage, 'rb')}
        data = {"providers": "google"}
        try: 
            response = requests.post(
                endpoint, data=data, files=files, headers=headers)
            result = json.loads(response.content)
            if result['google']['status'] == 'success': 
                isimagegetlabels = True
                for label in result['google']['items']:
                   if label["label"] not in moodimageobjects: 
                     moodimageobjects.append(label["label"])
                     objectsdata = {"object_name":label["label"],"moodboard_image_id":imageid }
                     create_moodboard_images_objects(db,objectsdata)  
                
            return moodimageobjects

        except: 
            return moodimageobjects
        
    except:
      return moodimageobjects  
    

async def generate_images(db,text_prompt,userid):
    generatedimages = [] 
    try:     
        headers = {"Authorization": "Bearer "+API_KEY}
        url = "https://api.edenai.run/v2/image/generation"
        payload = {
            "providers": "openai",
            "text": text_prompt,
            "resolution": "512x512",
            "num_images":4
        }
        response = requests.post(url, json=payload, headers=headers)
        result = json.loads(response.text)
        if result['openai']["status"] == "success": 
              for image in result['openai']['items']:
                #deletedatesbeforeoneday(userid)
                generatedimages.append(image["image_resource_url"]) 
              insertcurrentdate(db,userid)
                  
        return generatedimages
    except:  
        return generatedimages
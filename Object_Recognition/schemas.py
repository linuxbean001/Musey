from pydantic import BaseModel
from typing import Any, Union


class Users(BaseModel):
    name: str
    email: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True



class PasswordReset(BaseModel):
    password: str
    token: str

    class Config:
        orm_mode = True

class UserMoodboards(BaseModel):
    id: int

    class Config:
        orm_mode = True

class MoodboardWithImages(BaseModel):
    userid: int
    moodboardid: int
    moodboardprompt: str

    class Config:
        orm_mode = True


class UserCreate(Users):
    hashed_password: str


class User(Users):
    id: int

    class Config:
        orm_mode = True


class MoodBoard(BaseModel):
    title: Union[str, None] = None
    user_id: Union[str, None] = None
    images: list

    class Config:
        orm_mode = True


class MoodBoardTitleUpdate(BaseModel):
    title:str
    moodboard_id:int

    class Config:
        orm_mode = True
        
class RenderImages(BaseModel):
    prompt: Union[str, None] = None
    moodboard_id: Union[str, None] = None
    user_id: Union[str, None] = None
    images: list
    class Config:
        orm_mode = True

class UserSubcriptions(BaseModel):
    subscriptionid: Union[str, None] = None
    customerid: Union[str, None] = None
    user_id: Union[str, None] = None

    class Config:
        orm_mode = True


class MoodBoardCreate(MoodBoard):
    pass


class MoodBoardImages(BaseModel):
    image_url: list
    moodboard_id: int
    userid:int

    class Config:
        orm_mode = True

class MoodBoardRenders(BaseModel):
     moodid:int
     userid:int
     userrole:str 
     images:list
     prompt:str
     
     class Config:
      orm_mode = True

class MoodBoardDelete(BaseModel): 
    moodboard_id:int
    class Config: 
        orm_mode = True      

class MoodBoardImagesCreate(MoodBoardImages):
    pass


class MoodBoardImageObjects(BaseModel):
    object_name: str
    moodboard_image_id: str

    class Config:
        orm_mode = True


class MoodBoardImageObjectsCreate(MoodBoardImageObjects):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class SystemUser(Users):
    user: Users

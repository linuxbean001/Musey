from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = email = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(255))
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.utcnow)
    owner = relationship("MoodBoard", back_populates="moodboards")

    def __repr__(self):
        return '<User %r>' % (self.id)


class UserSubcriptions(Base):
    __tablename__ = "usersubcriptions"
    id = Column(Integer, primary_key=True, index=True)
    subscriptionid = Column(String(255))
    customerid = Column(String(255), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return '<UserSubcriptions %r>' % (self.id)


class MoodBoard(Base):
    __tablename__ = "moodboards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    join_date = Column(DateTime, default=datetime.utcnow)
    moodboards = relationship("Users", back_populates="owner")
    # moodboardimages = relationship("MoodBoardImages", back_populates="moodboardimages")
    def __repr__(self):
        return '<MoodBoard %r>' % (self.id)


class MoodBoardImages(Base):
    __tablename__ = "moodboardimages"
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255))
    join_date = Column(DateTime, default=datetime.today().date)
    counterid = Column(Integer)
    moodboard_id = Column(Integer, ForeignKey("moodboards.id"))
    # items = relationship("Users", back_populates="moodboardimageojects")

    def __repr__(self):
        return '<MoodBoardImage %r>' % (self.id)


class MoodBoardImagesRequestCount(Base):
    __tablename__ = "moodboardrequestcount"
    id = Column(Integer, primary_key=True, index=True)
    join_date = Column(DateTime, default=datetime.today().date)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return '<MoodBoardImagesRequestCount %r>' % (self.id)


class MoodBoardRenderImages(Base):
    __tablename__ = "moodboardrenderimages"
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255))
    join_date = Column(DateTime, default=datetime.today().date)
    moodboard_id = Column(Integer, ForeignKey("moodboards.id"))
    # items = relationship("Users", back_populates="moodboardimageojects") 
    def __repr__(self):
        return '<MoodBoardRenderImages %r>' % (self.id)


class MoodBoardImageObjects(Base):
    __tablename__ = "moodboardimageojects"
    id = Column(Integer, primary_key=True, index=True)
    object_name = Column(String(255))
    moodboard_image_id = Column(Integer, ForeignKey("moodboardimages.id"))

    def __repr__(self):
        return '<MoodBoardImageObject %r>' % (self.id)
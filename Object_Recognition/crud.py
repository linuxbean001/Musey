from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import desc
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.Users).filter(models.Users.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    return user

def get_moodboard_by_id(db: Session, id:int):
    moodboard = db.query(models.MoodBoard).filter(models.MoodBoard.id == id).first()
    return moodboard

def update_status_subcription(db: Session, subid):
    subdata = db.query(models.UserSubcriptions).filter(
        models.UserSubcriptions.subscriptionid == subid).first()
    if subdata is not None:
        subdata.is_active = 0
        db.commit()

def getimageobjects(db,id):
    imageobjects = []
    objectsdata =  db.query(models.MoodBoardImageObjects).filter(models.MoodBoardImageObjects.moodboard_image_id == id).all()
    return objectsdata 

def get_moodboards_by_userid(db: Session, user_id: int):
    try:
      moodboardswithimages = []
      moodboards =  db.query(models.MoodBoard).filter(models.MoodBoard.user_id == user_id).all()
      for moodboard in moodboards: 
          imagelist = []
          images  =  db.query(models.MoodBoardImages).filter(models.MoodBoardImages.moodboard_id == moodboard.id).all()
          if len(images)>0: 
            for image in images:
                objlist = []
                objs   =  db.query(models.MoodBoardImageObjects).filter(models.MoodBoardImageObjects.moodboard_image_id ==image.id).all()
                if len(objs)>0: 
                    for obj in objs:
                        objlist.append(obj.object_name)

                imagelist.append({"image_id":image.id,"image_url":image.image_url,"image_objects": objlist})
            moodboardswithimages.append({"moodboard_id":moodboard.id,"title":moodboard.title,"images":imagelist})
      if len(moodboardswithimages)<1: 
           return {"status":"success","moodboards":moodboardswithimages,"message":"No moodboards for user"}
      return {"status":"success","moodboards":moodboardswithimages,"message":""}
    except: 
        return {"status":"error","error":"Invalid User Id"}  
   

# def get_moodboardimages_by_moodboard_id(db: Session, moodboard_id: int):
#     return db.query(models.MoodBoardImages).filter(models.MoodBoardImages.moodboard_id == moodboard_id).first()


# def get_moodboardobjects_by_moodboard_image_id(db: Session, moodboard_image_id: int):
#     return db.query(models.MoodBoardImageObjects).filter(models.MoodBoardImageObjects.moodboard_image_id == moodboard_image_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    # fake_hashed_password = user.password + "notreallyhashed"
    try:
        db_user = models.Users(name=user.name, email=user.email,
                               hashed_password=user.hashed_password, role=user.role, is_active=user.is_active)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        pass
    return None


def create_useroth(db: Session, user):
    # fake_hashed_password = user.password + "notreallyhashed"
    try:
        db_user = models.Users(name=user['name'], email=user['email'],
                               hashed_password=user['hashed_password'], role=user['role'], is_active=user['is_active'])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        pass
    return None

def create_moodboard(db: Session, moodboard: schemas.MoodBoard):
    try:
        usermoodboards = db.query(models.MoodBoard).filter(
            models.MoodBoard.user_id == moodboard.user_id).all()
        usermoodboardexists = db.query(models.MoodBoard).filter(
            models.MoodBoard.user_id == moodboard.user_id).filter(
            models.MoodBoard.title == moodboard.title).first()
        print(usermoodboardexists)
        if usermoodboardexists is not None:
            return {"status": "error", "error": "Moodboard Already exists for user"}
        userrole = db.query(models.Users).filter(
            models.Users.id == moodboard.user_id).first()
        if usermoodboards is not None:
            if userrole.role == 'free':
                if len(usermoodboards) > 2:
                    return {"status": "error", "error": "Free user can only add 2 moodboard, please purchase prop plan to add more moodboards"}
            if len(usermoodboards) > 20:
                return {"error": "Pro user limit 20 reached"}
        db_moodboard = models.MoodBoard(
            title=moodboard.title, user_id=moodboard.user_id)
        db.add(db_moodboard)
        db.commit()
        db.refresh(db_moodboard)
        db_moodboard.error = None
        if db_moodboard is not None:
            return {"status": "success", "success": "MoodBoard created Successfully", "moodboardId": db_moodboard.id}
    except:
        return {"status": "error", "error": "Free user can only add 2 moodboard, please purchase prop plan to add more moodboards"}


def delete_moodboard(db,id): 
    try: 
        isdeleted = db.query(models.MoodBoard).filter(
                models.MoodBoard.id == id).first()
        if isdeleted is not None:
            delthis = db.get(models.MoodBoard, isdeleted.id)
            print(delthis)
            db.delete(delthis)
            db.commit()
            return {"status":"success","message":"Moodboard Successfully Deleted"}
        else:
            return {"status":"error","message":"Moodboard not exist"}
    except: 
        return {"status":"error","message":"Moodboard not exist"}       

def delete_images_by_moodboard(db: Session, moodboardid):
    try:
        isdeleted = db.query(models.MoodBoardImages).filter(
            models.MoodBoardImages.moodboard_id == moodboardid).all()
        if isdeleted is not None:
            for i in isdeleted:
                delete_objects_by_image(db,i.id)
                delthis = db.get(models.MoodBoardImages, i.id)
                print(delthis)
                db.delete(delthis)
                db.commit()
            return True
        else:
            return False
    except:
        return False  

def delete_objects_by_image(db: Session, imageid):
    try:
        isdeleted = db.query(models.MoodBoardImageObjects).filter(
            models.MoodBoardImageObjects.moodboard_image_id == imageid).all()
        if isdeleted is not None:
            for i in isdeleted:
                delthis = db.get(models.MoodBoardImageObjects, i.id)
                print(delthis)
                db.delete(delthis)
                db.commit()
            return True
        else:
            return False
    except:
        return False   
       
def insertcurrentdate(db:Session,userid): 
    db_moodboard_image_object =  models.MoodBoardImagesRequestCount(user_id=userid)
    db.add(db_moodboard_image_object)
    db.commit()
def getrequestsperday(db:Session,userid): 
    isdeleted = db.query(models.MoodBoardImagesRequestCount).filter(
            models.MoodBoardImagesRequestCount.user_id == userid).all()
    count = 0 
    try: 
        if len(isdeleted)>0:
            for i in isdeleted:
                if str(i.join_date).split()[0] == str(datetime.today().date()): 
                    count +=1 
                else: 
                    delthis = db.get(models.MoodBoardImagesRequestCount, i.id)
                    db.delete(delthis)
                    db.commit()
        return count        
    except: 
        pass            
    return count
# def delete_images_by_moodboard(db: Session, moodboardimageid):
def last_moodnoard_image_id(db:Session,moodboardid): 
     try: 
      lastindex = db.query(models.MoodBoardImages).filter(models.MoodBoardImages.moodboard_id ==moodboardid).order_by(desc(models.MoodBoardImages.id)).first()
      return {"status":"success","lastid":lastindex.counterid}
     except: 
         return {"status":"error","error":"The moodboard id is not correct"} 

def create_moodboard_image(db: Session, moodboardimage):
    db_moodboard_image = models.MoodBoardImages(
        image_url=moodboardimage["image"],counterid=moodboardimage["counterid"] ,moodboard_id=moodboardimage["moodboard_id"])
    db.add(db_moodboard_image)
    db.commit()
    db.refresh(db_moodboard_image)
    # print(db_moodboard_image)
    if db_moodboard_image is None:
        return {"status": "error", "error": "server error, please try again letter."}
    else:
        return {"status": "success", "moodboard_id": moodboardimage["moodboard_id"], "moodboard_image_id": db_moodboard_image.id, "url": db_moodboard_image.image_url}

def create_moodboard_images_objects(db:Session,objectsdata): 
    try:
        db_moodboard_image_object =  models.MoodBoardImageObjects(object_name=objectsdata["object_name"], moodboard_image_id=objectsdata["moodboard_image_id"])
        db.add(db_moodboard_image_object)
        db.commit()
        db.refresh(db_moodboard_image_object)
        return True
    except: 
        return False

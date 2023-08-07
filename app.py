from Object_Recognition.email import send_email, send_subscription_success, send_forgetpass
from fastapi.responses import HTMLResponse
import uvicorn
import os
from io import BytesIO
from PIL import Image, ImageFile
import requests
import json
import random
import string
import stripe
import base64
from typing import List
from fastapi import Depends, status, FastAPI, HTTPException, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Object_Recognition import crud, models, schemas
from Object_Recognition.database import SessionLocal, engine
from utils import (get_hashed_password, password_verification,
                   create_token, create_refresh_token, email_verify, userinfo,userinfoforpass, detectionimagesobjects,generate_images)
from deps import get_current_user
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from collections import defaultdict 
GOOGLE_CLIENT_ID = '560500420895-gp0nj2v6nlftuo2b4khk0o6i8dd62g0j.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
               'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET,
               'SESSION_COOKIE_SAMESITE': 'Lax'}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


models.Base.metadata.create_all(bind=engine)

stripe_keys = {
    "secret_key": 'sk_test_51MniNtSGd0ho6TQXnQbrlp0kgNjStFm3cNaJK5XQ3JVyL9ufbFg72xjQJ7RxzOQjeofJ2THQYBulTlKeXDgAnkmC00bwp2R3Uz',
    "publishable_key": 'pk_test_51MniNtSGd0ho6TQXHQ8Puew9Z1Mk1WVkXRruOE4g58O8U5tdTWZsgWXjTAhH9RmWSgta4USqjd8NupY3KMtXXsFF00DBojq5zE',
    "price_id": 'price_1NaFoXSGd0ho6TQXmpT5exyn',
    "endpoint_secret": 'whsec_f2e2e1f841a30271e66aedeb12ac084b42875968c7994268c6eeead451e5d870',
}

domainurl = "http://localhost:8000/"
#initialising an empty dict 
def def_value():
    return "Not Present"
      
# Defining the dict
objectsdict = defaultdict(def_value)

# from fastapi_sqlalchemy import DBSessionMiddleware, db


# from schemas import Users as SchemaUsers
# from schemas import MoodBoard as SchemaMoodBoard
# from schemas import MoodBoardImages as SchemaMoodBoardImages
# from schemas import MoodBoardImageObjects as SchemaMoodBoardImageObjects

# from schemas import Users
# from schemas import MoodBoard
# from schemas import MoodBoardImages
# from schemas import MoodBoardImageObjects


# from models import Users as ModelUsers
# from models import MoodBoard as ModelMoodBoard
# from models import MoodBoardImages as ModelMoodBoardImages
# from models import MoodBoardImageObjects as ModelMoodBoardImageObjects

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allows all origins
    allow_credentials=True,
    allow_methods=['*'],  # Allows all methods
    allow_headers=['*'],  # Allows all headers
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key='!myseckeyllt')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# to avoid csrftokenError


@app.post("/signup/", response_model=schemas.Users)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=200, detail="Email already registered")
    user.hashed_password = get_hashed_password(user.hashed_password)
    createuser = crud.create_user(db=db, user=user)
    if createuser != None:
        db_user_email = crud.get_user_by_email(db, email=user.email)
        if db_user_email != None:
            await send_email([db_user_email.email], db_user_email)
    return createuser


@app.get("/verification/", response_class=RedirectResponse)
async def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    user = await email_verify(db, token)
    if user is not None:
        user.is_active = True
        db.commit()
        redirect_url = 'http://localhost:3000/emailverified?message=verficationsuccess'
        return redirect_url
        # return {"Userverification": "User Successfully verified"}
    else:
        redirect_url = 'http://localhost:3000/emailverified?message=tokenexpired'
        return redirect_url


@app.get("/forgetpassword/")
async def forget_password(email: str):
    await send_forgetpass([email])
    return "password reset email sent"
# Tag it as "authentication" for our docs
@app.get('/logingoogle', tags=['authentication'])
async def login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth', response_class=RedirectResponse)
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except:
        redirect_url = 'http://localhost/test.php?accesstoken=no'
        return redirect_url
     # <=0.15
    # user = await oauth.google.parse_id_token(request, token)
    user = token['userinfo']
    print(user)
    print(user['email'])
    username = user['name']
    useremail = user['email']
    res = ''.join(random.choices(string.ascii_lowercase +
                                 string.digits, k=8))
    password = str(res)
    usertoregister = {
        "name": username,
        "email": useremail,
        "role": "free",
        "is_active": True,
        "hashed_password": password
    }

    login_token = ''
    db_user = crud.get_user_by_email(db, email=useremail)

    if db_user:
        login_token = create_token(db_user.email)
    else:
        user.hashed_password = get_hashed_password(password)
        createuser = crud.create_useroth(db=db, user=usertoregister)
        print(createuser)
        if createuser != None:
            db_user_email = crud.get_user_by_email(
                db, email=useremail)
            print(db_user_email)
        login_token = create_token(db_user_email.email)
    redirect_url = 'http://localhost:3000/?accesstoken='+login_token
    return redirect_url


@app.get("/user/", response_class=JSONResponse)
async def getuserfromtoken(request: Request, token: str, db: Session = Depends(get_db)):
    user = await userinfo(db, token)
    if user is not None:
        user.is_active = True
        db.commit()
        return {"userName": user.name, "userEmail": user.email, "userRole": user.role, "useractive": user.is_active, "UserId": user.id}
    else:
        return {"Userverification": "Token Expires"}


@app.get("/create-checkout-session")
def create_checkout_session(request: Request):
    stripe.api_key = stripe_keys["secret_key"]
    referid = 0

    try:
        referid = request.query_params['userid']
        checkout_session = stripe.checkout.Session.create(
            # you should get the user id here and pass it along as 'client_reference_id'
            #
            # this will allow you to associate the Stripe session with
            # the user saved in your database
            #
            # example: client_reference_id=user.id,
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            client_reference_id=referid,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": stripe_keys["price_id"],
                    "quantity": 1,
                }
            ],
            metadata={"planname": 'basic'}
        )

        return {"sessionId": checkout_session["id"]}
    except Exception as e:
        return {"error": "something went wrong"}


@app.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400
    if event["type"] == "checkout.session.completed":
        print(event['data'])
        try:
            session = event["data"]["object"]
            await handle_checkout_session(session, db)
        except:
            pass

    elif event["type"] == "invoice.payment_failed":
        print(event['data'])
        subscriptionid = event["data"]["object"]['subscription']
        try:
            crud.update_status_subcription(db, subscriptionid)
        except:
            pass

    elif event["type"] == "customer.subscription.deleted":
        print(event['data'])
        subscriptionid = event["data"]["object"]['id']
        try:
            crud.update_status_subcription(db, subscriptionid)
        except:
            pass
        pass


async def handle_checkout_session(session, db: Session = Depends(get_db)):
    print(session.client_reference_id, session.subscription, session.customer)
    usersubscribed = db.query(models.UserSubcriptions).filter(
        models.UserSubcriptions.user_id == int(session.client_reference_id)).first()

    if usersubscribed is None:
        useremail = crud.get_user(db, int(session.client_reference_id))
        usersubscribeddata = models.UserSubcriptions(
            subscriptionid=session.subscription, customerid=session.customer, user_id=session.client_reference_id, is_active=1)
        db.add(usersubscribeddata)
        useremail.role = 'pro'
        db.commit()
        await send_subscription_success([useremail.email])
        return "Subsciption created"


@ app.post('/login', summary="Create access and refresh tokens for user", response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=form_data.username)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = db_user.hashed_password
    if not password_verification(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if db_user is not None and db_user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify from email and if token expires register again"
        )

    return {
        "user_id": db_user.id,
        "email_address": db_user.email,
        "access_token": create_token(db_user.email),
        "refresh_token": create_refresh_token(db_user.email),
    }

   
@ app.post("/creatmoodboard/", response_class=JSONResponse)
def create_moodboard(moodboard: schemas.MoodBoard, db: Session = Depends(get_db)):
  try:
    imageslist = moodboard.images
    if imageslist is None:
        return {"status":"error","error":"Please try after uploading the images"}
    moodboardres = crud.create_moodboard(db=db, moodboard=moodboard)
    if moodboardres["status"] == "success" or moodboardres["status"] == "ismoodboard":
        moodid = moodboardres["moodboardId"]
        userid = moodboard.user_id
        detectionimages = {"images": []}
        i = 0
        for image in imageslist:
            nameofimage = 'image_' + \
                str(userid)+'_'+str(moodid)+'_' + \
                str(i)
            i += 1
            decodeimage = base64.b64decode(image.split(',')[1])
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            img = Image.open(BytesIO(decodeimage))
            img.save("static/moodimages/"+nameofimage+'.png', 'PNG')
            moodboardimageinsertion = {
                "moodboard_id": moodid, "image": nameofimage+".png","counterid":i}
            dbimage = crud.create_moodboard_image(
                db, moodboardimageinsertion)
            if dbimage["status"] == "success":
                imgobj = {
                    'image_id': dbimage["moodboard_image_id"],
                    'image_url': dbimage["url"],
                    'image_objects': []
                }
                detectionimages["images"].append(imgobj)
                # detectionimages["images"].append(dbimage["url"])
        if len(detectionimages["images"]) > 0:
            return {"status":"success","userid":userid,"moodid":moodid,"imagepath":"http://localhost:8000/static/moodimages/","uploadedimages":detectionimages}
            #generateimages = detectionimagesobjects(db, detectionimages,moodid,userid)
            
    else:
        return {"status":"error","error": moodboardres["error"]}
  except:
    return {"status":"error","error": "Something went wrong"}

@ app.post("/updatemoodboard/", response_class=JSONResponse)
def update_moodboardtitle(mooddata:schemas.MoodBoardTitleUpdate,db:Session=Depends(get_db)): 
        if type(mooddata.moodboard_id) == int: 
            print(mooddata)
            moodboard_data = crud.get_moodboard_by_id(db,mooddata.moodboard_id)
            print(moodboard_data)
            if moodboard_data is None: 
                
                return {"status":"error","error":"moodboard not exists with this id "}
            else: 
                if mooddata.title!='': 
                  moodboard_data.title =  mooddata.title
                  db.commit()
                  db.refresh(moodboard_data)  
                  return {"status": "success","moodboard_id":moodboard_data.id,"moodboard_title":moodboard_data.title,"message":"title successfuly updated"}


    # except: 
    #     return {"status":"error","error":"Please pass the correct moodboard id"}     
@app.post("/changepassword/",response_class=JSONResponse)
async def password_change(passdata: schemas.PasswordReset,db:Session=Depends(get_db)): 
 
        password = passdata.password
        emailtoken = passdata.token 
        user = await userinfoforpass(db, emailtoken)
        if user is not None: 
            user.hashed_password = get_hashed_password(password)
            db.commit()
            return {"status":"success","message":"Password Successfully Updated"}
        else: 
            return {"status":"error","message":"The token expired"}
    # except: 
    #     return {"status":"error","message":"The token expired"}
    
@app.post("/moodboardmoreimages/", response_class=JSONResponse)
def add_more_moodboard_images(moodboard: schemas.MoodBoardImages, db: Session = Depends(get_db)):
    try:
        imageslist = moodboard.image_url
        moodboardid = moodboard.moodboard_id
        userid = moodboard.userid
        if imageslist is None:
            return {"status":"error","error":"Please try after uploading the images"}
        last_image = crud.last_moodnoard_image_id(db,int(moodboard.moodboard_id))
        if last_image["status"] == "success":
            i = last_image["lastid"]
            detectionimages = {"images": []}
            for image in imageslist:
                nameofimage = 'image_' + \
                    str(userid)+'_'+str(moodboardid)+'_' + \
                    str(i)
                i += 1
                decodeimage = base64.b64decode(image.split(',')[1])
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                img = Image.open(BytesIO(decodeimage))
                img.save("static/moodimages/"+nameofimage+'.png', 'PNG')
                moodboardimageinsertion = {
                    "moodboard_id": moodboardid, "image": nameofimage+".png","counterid":i}
                dbimage = crud.create_moodboard_image(
                    db, moodboardimageinsertion)
                if dbimage["status"] == "success":
                    detectionimages["images"].append(dbimage["url"])
            if len(detectionimages["images"]) > 0:
                return {"status":"success","userid":userid,"moodid":moodboardid,"imagepath":"http://localhost:8000/static/moodimages/","uploadedimages":detectionimages}
                #generateimages = detectionimagesobjects(db, detectionimages,moodid,userid)
        

    except: 
         return {"status":"error","error":"something went wrong uploading images"}
    
#     # pass 
# @app.post("/renderimages", response_class=JSONResponse)
# def getimages():
#     # 
#     pass  
#   
# Linuxbean@5455  
@app.post("/userupdate/", response_class=JSONResponse)
def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        if type(user.id) != int:
            return {"error", "Invalid User id"}
        else:
            db_user = crud.get_user(db, user.id)
            if db_user is not None:
                db_user.name = user.name
                # db_user.email = user.email
                # user.hashed_password = get_hashed_password(
                #     user.hashed_password)
                db.commit()
                db.refresh(db_user)
        return {"success": "User Updated Successfully", "userName": db_user.name, "email": db_user.email}
    except:
        return {"error", "something went wrong updating user"}
    

@app.post("/renderimages", response_class=JSONResponse)
async def render_images(imagesdata:schemas.MoodBoardRenders,db:Session = Depends(get_db)): 
   try:  
    if len(imagesdata.images)>0:
        moodboard_id = imagesdata.moodid
        user_id = imagesdata.userid
        prompt  =  imagesdata.prompt
        userrole = imagesdata.userrole
        if userrole == 'free': 
         requestcount = crud.getrequestsperday(db,user_id)
         if requestcount>4: 
             return {"status":"error","error":"User limit reached for the today"}
        responsedata = {"user_id":user_id,"moodboard_id":moodboard_id,"imageswithobjects":[],"generatedimages":[]}
        mergedobjects = []

        for image in  imagesdata.images: 
            image_url = image["image_url"]
            image_id = image["image_id"]
            imgobjs = image["image_objects"]
            imgobjects = []
            # 
            if len(imgobjs)>0:  
              print("Objects detected") 
              for obj in imgobjs: 
                  if obj not in mergedobjects:
                      mergedobjects.append(obj)
                      imgobjects.append(obj)
                      
            else: 
                print("Objects not detected") 
                imgobjects = await detectionimagesobjects(db,image_url,image_id,moodboard_id,user_id)
                if(len(imgobjects)>0):
                    for obj in imgobjects: 
                        if obj not in mergedobjects:
                           mergedobjects.append(obj)
                           imgobjects.append(obj)
            fnobj=[]                                    
            for mg_object in imgobjects: 
                if mg_object not in fnobj:
                    fnobj.append(mg_object)                        
                   #currdict[image_id].append(img_object)  
            responsedata["imageswithobjects"].append({"imageurl":image_url,"image_id": image_id,"imgobjects":fnobj})
        if len(mergedobjects)>0: 
            prompt = prompt+' '+' '.join(mergedobjects)
            images = await generate_images(db,prompt,user_id)
        else: 
            images = await generate_images(db,prompt,user_id)

        responsedata["generatedimages"] = images 
        responsedata["status"] = "success"
        return responsedata
   except:
     return {"status":"error","error":"Api taking time due to high traffic, please try again" }

@app.get("/")
def index():
    return {"Backend Procedure with hidden routes"}

def fake_hash_password(password: str):
    return "fakehashed" + password

@app.post("/usermoodboards",response_class=JSONResponse)
def getmoodboards(user: schemas.UserMoodboards,db:Session = Depends(get_db)):
    try:
        userid = user.id
        if type(user.id) != int:
            return {"status":"error","error":"Invalid User id"}
        
        return crud.get_moodboards_by_userid(db,userid)
    except: 
        return {"status":"error","error":"Incorrect User Id"}

@app.post("/deletemoodboard",response_class=JSONResponse)
def deletemoodmoard(moodboard: schemas.MoodBoardDelete,db:Session = Depends(get_db)):
    try:
        moodboard_id = moodboard.moodboard_id
        if type(moodboard.moodboard_id) != int:
            return {"status":"error","error":"Invalid User id"}
        else: 
          is_data_deleted =  crud.delete_images_by_moodboard(db,moodboard_id)
          if is_data_deleted == True: 
            return crud.delete_moodboard(db,moodboard_id)
    except: 
         return {"status":"error","message":"Moodboard not exist"}
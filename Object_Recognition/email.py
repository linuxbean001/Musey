from fastapi import (BackgroundTasks, UploadFile, File,
                     Form, Depends, HTTPException, status)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
from .models import Users
from jose import jwt
from datetime import timedelta, datetime
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

conf = ConnectionConfig(
    MAIL_USERNAME="217c9f2c5654b0",
    MAIL_PASSWORD="1596d2071a2d5f",
    MAIL_FROM="test@email.com",
    MAIL_PORT=2525,
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def send_email(email: EmailSchema, instance: Users):
    expires_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "exp": expires_time,
        "id": instance.id,
        "username": instance.email
    }
    token = jwt.encode(token_data, "mtoken")

    template = f"""
                <!DOCTYPE html>
                <html lang="en">
                    <body>
                        <div class="display:flex;align-items:center;justify-content:center;flex-direction:column">
                            <h2>Thank you for registering to our website, Enter following verification code to verify your account</h2>
                            <h1" style="text-decoration:none;margin-top:1rem;font-size:1rem;background:red;color:#fff;padding:5px 10px"><a href='http://localhost:8000/verification?token={token}'>Verify Email</a></h1> 
                        </div>
                    </body>
                </html>
                """
    message = MessageSchema(
        subject="MoodBoardAI Account Verification Email",
        recipients=email,
        body=template,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)

async def send_subscription_success(email: EmailSchema):
    template = f"""
                <!DOCTYPE html>
                <html lang="en">
                    <body>
                        <div class="display:flex;align-items:center;justify-content:center;flex-direction:column">
                            <h2>Thank you for subscribing to Website</h2>
                            <p>Login to Website and use unlocked services</p>
                        </div>
                    </body>
                </html>
                """
    print(template)
    message = MessageSchema(
        subject="MoodBoardAI Successful Subscription",
        recipients=email,
        body=template,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)

async def send_forgetpass(email: EmailSchema):

    expires_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "exp": expires_time,
        "emailuser":email
    }
    token = jwt.encode(token_data, "rptoken")
    template = f"""
                <!DOCTYPE html>
                <html lang="en">
                    <body>
                        <div class="display:flex;align-items:center;justify-content:center;flex-direction:column">
                            <h2>CLick Reset password to reset the password</h2>
                            <h1" style="text-decoration:none;margin-top:1rem;font-size:1rem;background:red;color:#fff;padding:5px 10px"><a href='http://localhost:3000/passwordchange?password={token}'>Reset Password</a></h1> 
                        </div>
                    </body>
                </html>
                """
    print(template)
    message = MessageSchema(
        subject="MoodBoardAI Reset Password",
        recipients=email,
        body=template,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
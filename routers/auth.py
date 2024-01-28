from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
from utils import verify_password, hash_password
import oauth2
from fastapi.responses import RedirectResponse, Response
from typing import Dict
 
templates = Jinja2Templates(directory="templates")
router = APIRouter(
    tags = ['Authentification']  
)

@router.get("/")
def read_root(request: Request):
    cookie = request.cookies.get("access_token")
    if not cookie:
        return templates.TemplateResponse(name="index.html", context={"request": request})
    else:
        try:
            oauth2.verify_access_token(cookie, credentials_exception=HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"))
            return templates.TemplateResponse(name="home.html", context={"request": request})
        except:
            return templates.TemplateResponse(name="index.html", context={"request": request})
 
 
@router.get('/login')
async def login_page(request: Request):
    return templates.TemplateResponse(name="login.html", context={"request": request})
 
@router.post('/login', response_model=schemas.Token)
async def login(
    response: Response,       
    request: Request,     
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
   
    ############################
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    ############################
   
   
    access_token = oauth2.create_access_token(data={"user_email": user.email, "user_id": user.id})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token)
   
   
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/login_form', response_model=schemas.Token)
async def login_form(
response: Response,       
    request: Request,     
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
   
    ############################
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    ############################
   
   
    access_token = oauth2.create_access_token(data={"user_email": user.email, "user_id": user.id})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token)
   
   
    return response

@router.get('/register')
async def register_page(request: Request):
    return templates.TemplateResponse(name="register.html", context={"request": request})
 
@router.post("/register", response_model=schemas.UserOut)
async def create_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):

    hashed_password = hash_password(password)
    password = hashed_password
    new_user = models.User(email=email, password=password)
    db.add(new_user)
    db.commit()    
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get('/change_password')
async def change_password_page(request: Request):
    return templates.TemplateResponse(name="change_password.html", context={"request": request})
 
@router.post('/change_password', response_model=schemas.UserOutAfterPasswordChange)
async def change_password(new_password: str = Form(...), current_password: str = Form(...), current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    if not verify_password(current_password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
   
    user.password = hash_password(new_password)
    try:
        db.commit()
        db.refresh(user)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong, please try again later!")
    return schemas.UserOutAfterPasswordChange(email=user.email, msg="Password changed successfully")
 
@router.get("/logout")
async def logout(response: Response, request: Request):
    response = templates.TemplateResponse(name="index.html", context={"request": request})
    response.delete_cookie(key="access_token")

    return response
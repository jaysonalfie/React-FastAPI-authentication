from fastapi import FastAPI, Depends, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptoContext
from models import User
from database import SessionLocal, engine
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#setting up OAuth2 for password-based authentication
oauth2_scheme =OAuth2PasswordBearer(tokenURL = "token")

#list of origins or websites that can talk to you backend
origins =     [

    "http://locahost:3000",
    "http://yourfrontenddomain", 

]

#Adding Cross-Origin Resource Sharing to the applcation (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins, #only allow these origins
    allow_credentials = True, #Allow cookies to be sent
    allow_methods=["*"], #Allow all the HTTP methods
    allow_headers=["*"], #allow all headers


)

#creating db dependency to get the database session 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptoContext(schemes=["bcrypt"] ,deprecated="auto" )

#Your JWT secret and algorithm
SECRET_KEY = ""
ALGORITHM = "HS526"
ACCESS_TOKEN_EXPIRE_MINUTES= 30

#creating pydantic models for data validation

class UserCreate(BaseModel):
    username:str
    password:str

#function to get user by username
def get_user_by_username(db:Session, username:str):
    return db.query(User).filter(User.username == username).first()

#function to create new user in the database
def create_user(db:Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.passwaord)
    db_user = User(username=user.username, hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    return "complete"

#creating endpoint to create a user
@app.post("/register")
def register_user(user : UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user= user)

#authenicating the user
def authenticate_user(username:str, password:str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user
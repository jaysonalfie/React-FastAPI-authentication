from fastapi import FastAPI, Depends, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from models import User
from database import SessionLocal, engine
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#setting up OAuth2 for password-based authentication
oauth2_scheme =OAuth2PasswordBearer(tokenUrl = "token")

#list of origins or websites that can talk to you backend
origins =     [

    "http://localhost:3000",
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

pwd_context = CryptContext(schemes=["bcrypt"] ,deprecated="auto" )

#Your JWT secret and algorithm
SECRET_KEY = "fc2847411328aaac63a1378358086caccff1f423ee3be1cca7b43800e5a39c16"
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
    hashed_password = pwd_context.hash(user.password)
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

#creating the access token
def create_access_token(data:dict, expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#endpoint to the token
#will be used to handle login requests and issue tokens
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #authenticates user using username and password
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException (
             status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    #set expiration time for the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #creates a jwt token for the authenticated user
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}

#function to verify the token

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        #DEcode theJWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #extracting username from the token's payload
        username:str = payload.get("sub")
        #check if username exists in the token's payload
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail = "Token is invalid or expired")
    
#endpoint ot verify the token
@app.get("/verify-token/{token}")
async def verify_user_token(token:str):
    verify_token(token=token)
    return {"message": "Token is valid"} 
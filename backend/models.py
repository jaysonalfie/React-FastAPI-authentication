from sqlalchemy import Column, Integer , String
from database import Base
from database import engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index=True)
    username = Column(String(50), unique = True, index=True)
    hashed_password = Column(String(80))



User.metadata.create_all(bind=engine)
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
import models
from models import User
from database import engine , SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependancy = Annotated[Session, Depends(get_db)]

class User_Request(BaseModel):
    name: str = Field(min_length=1 , max_length=50)
    email: str = Field(min_length=5 , max_length=100)
    is_active: bool = True



@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependancy):
    return db.query(User).all()


@app.get("/user/{user_id}", status_code= status.HTTP_200_OK)
async def read_by_id(db: db_dependancy, user_id:int = Path(gt=0)): 
    user_models = db.query(User).filter(User.id == user_id).first()
    if user_models is not None:
        return user_models
    raise HTTPException(status_code=404, detail="User not found")



@app.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependancy , user_request: User_Request):
    user_models = User(**user_request.model_dump())
    db.add(user_models)
    db.commit()


@app.put("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def udate_users(db: db_dependancy,  user_request: User_Request, user_id: int = Path(gt=0)):


    user_models = db.query(User).filter(User.id == user_id).first()
    if user_models is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_models.name = user_request.name
    user_models.email = user_request.email
    user_models.is_active = user_request.is_active

    db.add(user_models)
    db.commit()



@app.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependancy, user_id: int = Path(gt=0)):
    user_models = db.query(User).filter(User.id == user_id).first()
    if user_models is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.query(User).filter(User.id == user_id).delete()
    db.commit()





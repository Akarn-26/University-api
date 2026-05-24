from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from university_db import create_tables, database  

# constants and setup
SECRET_KEY = "supersecretkey123"
pwd_context = CryptContext(schemes=["bcrypt"])
security = HTTPBearer()

# create tables before app starts
create_tables()

# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

# app
app = FastAPI(lifespan=lifespan)

class UserSchema(BaseModel):
    username:str
    password:str

class UniversitySchema(BaseModel):
    name:str
    country:str
    rank:int
    score: Optional[float]=None

class ReviewSchema(BaseModel):
    comment:str
    rating:float

async def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token=credentials.credentials
    try:
        data=jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="invalid token")
    
    user=await database.fetch_one("Select * from users where username=:username", {"username":data["sub"]})

    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    return user
@app.get("/")
async def start():
    return {"Message":"welcome to university db api"}

@app.post("/register")
async def register(user:UserSchema):

    existing=await database.fetch_one("Select * from users where username=:username", {"username":user.username})

    if existing:
        raise HTTPException(status_code=401, detail="Username already taken")
    hashed=pwd_context.hash(user.password)
    await database.execute("Insert into users (username, password) values (:username, :password)", {"username":user.username, "password":hashed})
    return {"message":"Registered Successfully"}

@app.post("/login")
async def login(user:UserSchema):
    existing=await database.fetch_one("Select * from users where username=:username",{"username":user.username})
    if not existing:
        raise HTTPException(status_code=401, detail="Username not found" )
    if not pwd_context.verify(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token=jwt.encode({"sub":user.username}, SECRET_KEY, algorithm="HS256")
    return {"Access Token": token}

@app.post("/universities")
async def add_university(university:UniversitySchema,user=Depends(get_current_user)):
    await database.execute("Insert into universities (name,country,rank,score) values (:name, :country,:rank, :score)", {"name":university.name, "country":university.country, "rank":university.rank, "score":university.score})
    return {"Message":"University Successfully Added"}

@app.get("/universities")
async def get_universities(country:Optional[str]=None):
    query="Select * from universities where 1=1"
    params={}
    if country:
        query+=" AND country=:country"
        params["country"]=country
    result=await database.fetch_all(query,params)
    return result

@app.post("/reviews/{uni_id}")
async def write_review(uni_id:int,review:ReviewSchema, user=Depends(get_current_user)):
    await database.execute("Insert into reviews (user_id,university_id, comment, rating) values (:user_id,:uni_id,:comment,:rating)", {"user_id":user["id"],"uni_id":uni_id, "comment":review.comment, "rating":review.rating})
    return {"message":"review successfully added"}

@app.get("/universities/{id}")
async def get_reviews(id:int):
    ans=await database.fetch_one("SELECT universities.*, AVG(reviews.rating) as avg_rating FROM universities LEFT JOIN reviews ON universities.id = reviews.university_id WHERE universities.id = :id",{"id":id})
    return ans

@app.get("/reviews/{uni_id}")
async def get_reviews(uni_id:int):
    ans=await database.fetch_all("Select users.username, reviews.comment, reviews.rating from reviews join users on reviews.user_id=users.id where reviews.university_id=:uni_id", {"uni_id":uni_id})
    return ans
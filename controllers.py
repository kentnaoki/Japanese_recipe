#from tkinter import image_names
from fastapi import FastAPI, Form, Depends, HTTPException, status
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials

from starlette.status import HTTP_401_UNAUTHORIZED

import database
from models import User, Item

import hashlib

import re

from mycalendar import MyCalendar
from datetime import datetime, timedelta
from auth import auth

from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import requests
import json
from typing import Optional
import time

from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

from bs4 import BeautifulSoup

from fastapi import File, UploadFile

from typing import List

from urllib import response
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

app = FastAPI(
    title = "Japanese food recipe",
    description = "Authentic Japanese food recipe for people who live outside Japan",
    version = "1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")


pattern = re.compile(r'\w{4,20}')  # 任意の4~20の英数字を示す正規表現
pattern_pw = re.compile(r'\w{6,20}')  # 任意の6~20の英数字を示す正規表現
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')


templates = Jinja2Templates(directory="templates")
jinja_env = templates.env


url_category = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1082013691690447331"
api_category = requests.get(url_category).json()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Category:
        def __init__(self, categoryName, categoryId):
            self.categoryName = categoryName
            self.categoryId = categoryId

        def add_imageUrl(self, imageUrl):
            self.imageUrl = imageUrl

class Recipe:
        def __init__(self, foodImageUrl, recipeId, recipeIndication, recipeTitle, recipeUrlId, recipeDescription):
            self.foodImageUrl = foodImageUrl
            self.recipeId = recipeId
            self.recipeIndication = recipeIndication
            self.recipeTitle = recipeTitle
            self.recipeUrlId = recipeUrlId
            self.recipeDescription = recipeDescription

        def add_recipe(self):
            Recipe.recipe_list.append(self)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):

    # list of objects of category
    categories = []

    # Large Category
    for index, category_json in enumerate(api_category["result"]["large"]):
        translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": category_json["categoryName"], }, )
        categoryName = translate_api.json()["translations"][0]["text"]
        category = Category(categoryName, int(category_json["categoryId"]))

        db_image = crud.get_image_large(db=db, scale="large", image_number=category.categoryId)
        #data = f'./images/images_large/{category.categoryId}.jpg'
        '''f = open(f'./images/images_large/{category.categoryId}.txt', 'r')
        data = f.read()
        f.close()'''
        category.add_imageUrl(db_image)
        categories.append(category)
        categories[index] = category
        
    
    return templates.TemplateResponse("index.html", {"request": request, "categories": categories} )

@app.get("/large", response_class=HTMLResponse)
async def read_large(request: Request, large_categoryId: int):

    for large_category_json in api_category["result"]["large"]:
        if int(large_category_json["categoryId"]) == large_categoryId:
            translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": large_category_json["categoryName"], }, )
            categoryName = translate_api.json()["translations"][0]["text"]
        else:
            pass  
    rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}"
    rankingUrl_Json = requests.get(rankingUrl_Json).json()
    Json_result = rankingUrl_Json["result"]

    Recipe.recipe_list = []
    
    for rec in Json_result:
        recipeUrlId = int(rec["recipeUrl"].split('/')[-2])
        translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
        recipeTitle = translate_api_title.json()["translations"][0]["text"]
        translate_api_description = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
        recipeDescription = translate_api_description.json()["translations"][0]["text"]
        recipe = Recipe(rec["mediumImageUrl"], rec["recipeId"], rec["recipeIndication"], recipeTitle, recipeUrlId, recipeDescription)
        recipe.add_recipe()
    
    rankingRecipe = Recipe.recipe_list

    return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe, "categoryName": categoryName})


@app.get("/medium", response_class=HTMLResponse)
def read_medium(request: Request, medium_categoryId: Optional[int] = None):

    if medium_categoryId == None:
        # list of objects of category
        mediumCategories = []

        # Large Category
        for index, category_json in enumerate(api_category["result"]["medium"]):
            translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": category_json["categoryName"], }, )
            categoryName = translate_api.json()["translations"][0]["text"]
            category = Category(categoryName, int(category_json["categoryId"]))
            f = open(f'./images/images_medium/{category.categoryId}.txt', 'r')
            data = f.read()
            f.close()
            category.add_imageUrl(data)
            mediumCategories.append(category)
            mediumCategories[index] = category

        return templates.TemplateResponse("medium.html", {"request": request, "mediumCategories": mediumCategories})

    else:
        for medium_category_json in api_category["result"]["medium"]:
            if medium_category_json["categoryId"] == medium_categoryId:
                mediumUrl = medium_category_json["categoryUrl"]
                id = int((mediumUrl.split('/')[-2]).split('-')[0])
                translate_api_categoryName = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": medium_category_json["categoryName"], }, )
                categoryName = translate_api_categoryName.json()["translations"][0]["text"]
            else:
                pass
        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{medium_categoryId}"
        rankingUrl_Json = requests.get(rankingUrl_Json).json()
        Json_result = rankingUrl_Json["result"]

        Recipe.recipe_list = []
        
        for rec in Json_result:
            recipeUrlId = int(rec["recipeUrl"].split('/')[-2])
            translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
            recipeTitle = translate_api_title.json()["translations"][0]["text"]
            translate_api_description = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
            recipeDescription = translate_api_description.json()["translations"][0]["text"]
            recipe = Recipe(rec["mediumImageUrl"], rec["recipeId"], rec["recipeIndication"], recipeTitle, recipeUrlId, recipeDescription)
            recipe.add_recipe()
        
        rankingRecipe = Recipe.recipe_list

        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe, "categoryName": categoryName})

@app.get("/small", response_class=HTMLResponse)
async def read_small(request: Request, small_categoryId: Optional[int] = None):

    if not small_categoryId:
        # list of objects of category
        smallCategories = []

        # Large Category
        for index, category_json in enumerate(api_category["result"]["small"]):
            translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": category_json["categoryName"], }, )
            categoryName = translate_api.json()["translations"][0]["text"]
            category = Category(categoryName, category_json["categoryId"])
            f = open(f'./images/images_small/{category.categoryId}.txt', 'r')
            data = f.read()
            f.close()
            category.add_imageUrl(data)
            smallCategories.append(category)
            smallCategories[index] = category

        return templates.TemplateResponse("small.html", {"request": request, "smallCategories": smallCategories})
    
    else:
        for small_category_json in api_category["result"]["small"]:
            if small_category_json["categoryId"] == small_categoryId:
                smallUrl = small_category_json["categoryUrl"]
                id = int((smallUrl.split('/')[-2]).split('-')[0])
                mediumId = int((smallUrl.split('/')[-2]).split('-')[1])
                translate_api_categoryName = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": small_category_json["categoryName"], }, )
                categoryName = translate_api_categoryName.json()["translations"][0]["text"]
            else:
                pass

        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{mediumId}-{small_categoryId}"
        rankingUrl_Json = requests.get(rankingUrl_Json).json()
        Json_result = rankingUrl_Json["result"]

        Recipe.recipe_list = []
        
        for rec in Json_result:
            recipeUrlId = int(rec["recipeUrl"].split('/')[-2])
            translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
            recipeTitle = translate_api_title.json()["translations"][0]["text"]
            translate_api_description = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
            recipeDescription = translate_api_description.json()["translations"][0]["text"]
            recipe = Recipe(rec["mediumImageUrl"], rec["recipeId"], rec["recipeIndication"], recipeTitle, recipeUrlId, recipeDescription)
            recipe.add_recipe()
        
        rankingRecipe = Recipe.recipe_list

        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe, "categoryName": categoryName})

@app.get("/recipe", response_class=HTMLResponse)
async def recipe(request: Request, recipeUrlId: int):
    url = f'https://recipe.rakuten.co.jp/recipe/{recipeUrlId}/'
    res = requests.get(url)

    soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')

    # make dictionary of materials
    items = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_name")
    servings = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_serving")
    materials = {}

    for item, serving in zip(items, servings):
        item_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": item.text.replace('\n', ''), }, )
        item_translated = item_api.json()["translations"][0]["text"]
        serving_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": serving.text.replace('\n', ''), }, )
        serving_translated = serving_api.json()["translations"][0]["text"]
        materials[item_translated] = serving_translated

    description = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_howto.section_border_top.section_padding_top.mt32.mb21 > ol > li > span.recipe_howto__text")
    descriptions = {}

    for index, item_description in enumerate(description):
        description_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": item_description.text.replace('\n', ''), }, )
        description_translated = description_api.json()["translations"][0]["text"]
        descriptions[index+1] = description_translated
    
    image = soup.select("#recipeBasic > div.recipe_info_img > img[src]")
    for i in image:
        imageUrl = i.get("src")

    recipeName_soup = soup.select("#recipeDetailTitle > h1")
    recipeName = recipeName_soup[0].text.split(' ')[0]
    recipeName_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": recipeName, }, )
    recipeName = recipeName_api.json()["translations"][0]["text"]

    return templates.TemplateResponse("recipe.html", {"request": request, "materials": materials, "descriptions": descriptions, "imageUrl": imageUrl, "recipeName": recipeName},)
    
@app.post("/images/large/", response_model=schemas.Image)
def create_image_large(image: schemas.Image, db: Session = Depends(get_db)):
    
    return crud.create_image_large(db, image=image)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

'''
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "8c0bbebdbe4a1f7b81efe51986fe98e05b90968738e6c43e4d9da3874c547eec"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

def fake_hash_password(password: str):
    return "fakehashed" + password

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user'''

@app.get("/register-login", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request,} )



'''security = HTTPBasic()

def admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # Basic認証で受け取った情報

    username = auth(credentials)
    password = hashlib.md5(credentials.password.encode()).hexdigest()
    # データベースからユーザ名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    task = db.session.query(Task).filter(Task.user_id == user.id).all()
    db.session.close()

    """ [new] 今日の日付と来週の日付"""
    today = datetime.now()
    next_w = today + timedelta(days=7)  #１週間後の日付

    # 該当ユーザがいない場合
    if user is None or user.password != password:
        error = 'ユーザ名かパスワードが間違っています．'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
        )
    
    """ [new] カレンダー関連 """
    # カレンダーをHTML形式で取得
    cal = MyCalendar(username,
                     {t.deadline.strftime('%Y%m%d'): t.done for t in task})  # 予定がある日付をキーとして渡す
 
    cal = cal.formatyear(today.year, 4)  # カレンダーをHTMLで取得

    # 直近のタスクだけでいいので、リストを書き換える
    task = [t for t in task if today <= t.deadline <= next_w]
    links = [t.deadline.strftime('/todo/'+username+'/%Y/%m/%d') for t in task]  # 直近の予定リンク
 
    return templates.TemplateResponse('admin.html',
                                      {'request': request,
                                       'user': user,
                                       'task': task,
                                       'links': links,
                                       "calendar": cal
                                       })

async def register(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("register.html",
                                    {"request": request,
                                    "username": "",
                                    "error": []})
    if request.method == "POST":
        data = await request.form()
        username = data.get("username")
        password = data.get("password")
        password_tmp = data.get("password_tmp")
        mail = data.get("mail")

        error = []

        tmp_user = db.session.query(User).filter(User.username == username).first()

        if tmp_user is not None:
            error.append('同じユーザ名のユーザが存在します。')
        if password != password_tmp:
            error.append('入力したパスワードが一致しません。')
        if pattern.match(username) is None:
            error.append('ユーザ名は4~20文字の半角英数字にしてください。')
        if pattern_pw.match(password) is None:
            error.append('パスワードは6~20文字の半角英数字にしてください。')
        if pattern_mail.match(mail) is None:
            error.append('正しくメールアドレスを入力してください。')
 
        # エラーがあれば登録ページへ戻す
        if error:
            return templates.TemplateResponse('register.html',
                                              {'request': request,
                                               'username': username,
                                               'error': error})
 
        # 問題がなければユーザ登録
        user = User(username, password, mail)
        db.session.add(user)
        db.session.commit()
        db.session.close()
 
        return templates.TemplateResponse('complete.html',
                                          {'request': request, 
                                          "username": username})

def detail(request: Request, username, year, month, day, credentials: HTTPBasicCredentials = Depends(security)):
    
    username_tmp = auth(credentials)

    if username_tmp != username:
        return RedirectResponse('/')
    
    user = db.session.query(User).filter(User.username == username).first()
    
    task = db.session.query(Task).filter(Task.user_id == user.id).all()
    db.session.close()

    theday = '{}{}{}'.format(year, month.zfill(2), day.zfill(2))  # 月日は0埋めする
    task = [t for t in task if t.deadline.strftime('%Y%m%d') == theday]

    return templates.TemplateResponse('detail.html',
                                      {'request': request,
                                       'username': username,
                                       'task': task,
                                       'year': year,
                                       'month': month,
                                       'day': day})

async def done(request: Request, credentials: HTTPBasicCredentials = Depends(security)):

    username = auth(credentials)

    user = db.session.query(User).filter(User.username == username).first()

    task = db.session.query(Task).filter(Task.user_id == user.id).all()

    data = await request.form()
    t_dones = data.getlist('done[]')

    for t in task:
        if str(t.id) in t_dones:
            t.done = True

    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')

async def add(request: Request, credentials: HTTPBasicCredentials = Depends(security)):

    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()
    
    # フォームからデータを取得
    data = await request.form()
    
    year = int(data['year'])
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data['hour'])
    minute = int(data['minute'])
 
    deadline = datetime(year=year, month=month, day=day,
                        hour=hour, minute=minute)
 
    # 新しくタスクを生成しコミット
    task = Task(user.id, data['content'], deadline)
    db.session.add(task)
    db.session.commit()
    db.session.close()
 
    return RedirectResponse('/admin')

def delete(request: Request, t_id, credentials: HTTPBasicCredentials = Depends(security)):

    username = auth(credentials)

    user = db.session.query(User).filter(User.username == username).first()

    task = db.session.query(Task).filter(Task.id == t_id).first()

    if task.user_id != user.id:
        return RedirectResponse('/admin')

    db.session.delete(task)
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')

def get(request: Request, credentials: HTTPBasicCredentials = Depends(security)):

    username = auth(credentials)

    user = db.session.query(User).filter(User.username == username).first()
    task = db.session.query(Task).filter(Task.user_id == user.id).all()

    db.session.close()

    task = [{
        'id': t.id,
        'content': t.content,
        'deadline': t.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'published': t.date.strftime('%Y-%m-%d %H:%M:%S'),
        'done': t.done,
    } for t in task]

    return task

async def insert(request: Request, content: str = Form(...), deadline: str = Form(...), credentials: HTTPBasicCredentials= Depends(security)):
    username = auth(credentials)
 
    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()
 
    # タスクを追加
    task = Task(user.id, content, datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S'))
 
    db.session.add(task)
    db.session.commit()
 
    # テーブルから新しく追加したタスクを取得する
    task = db.session.query(Task).all()[-1]
    db.session.close()
 
    # 新規タスクをJSONで返す
    return {
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'published': task.date.strftime('%Y-%m-%d %H:%M:%S'),
        'done': task.done,}'''
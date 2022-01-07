from fastapi import FastAPI
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import db
from models import User, Task
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from starlette.status import HTTP_401_UNAUTHORIZED

import db
from models import User, Task

import hashlib

import re
import requests

pattern = re.compile(r"\w{4,20}")
pattern_pw = re.compile(r"\w{6,20}")
pattern_mail = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")

app = FastAPI(
    title = "Japanese food recipe",
    description = "Authentic Japanese food recipe for people who live outside Japan",
    version = "0.9 beta"
)

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env

def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}, )

security = HTTPBasic()

def admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # Basic認証で受け取った情報
    username = credentials.username
    password = hashlib.md5(credentials.password.encode()).hexdigest()

    # データベースからユーザ名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    task = db.session.query(Task).filter(Task.user_id == user.id).all() if user is not None else []
    db.session.close()

    # 該当ユーザがいない場合
    if user is None or user.password != password:
        error = 'user name or password is wrong'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
        )

    
    # 特に問題がなければ管理者ページへ
    return templates.TemplateResponse('admin.html',
                                      {'request': request,
                                       'user': user,
                                       'task': task})

async def recipe(request: Request):
    url = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1082013691690447331"
    api = requests.get(url).json()
    return api

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
            error.append("This name is already used")
        if password != password_tmp:
            error.append("The password is wrong")
        if pattern.match(username) is None:
            error.append("Username has to be more than 4 characters and less than 20 characters.")
        if pattern_pw.match(password) is None:
            error.append("Password has to be more than 6 characters and less than 20 characters.")
        if pattern_mail.match(mail) is None:
            error.append("Enter correct email address")

        if error:
            return templates.TemplateResponse("register.html", 
                                            {"request": request,
                                            "username": username,
                                            "error": error})

        user = User(username, password, mail)
        db.session.add(user)
        db.session.commit()
        db.session.close()

        return templates.TemplateResponse("complete.html", 
                                        {"request": request,
                                        "username": username})
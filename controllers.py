#from tkinter import image_names
from fastapi import FastAPI, Form, Depends, HTTPException, status
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials

from starlette.status import HTTP_401_UNAUTHORIZED

import database

import hashlib

import re

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
import cv2

app = FastAPI(
    title = "Japanese food recipe",
    description = "Authentic Japanese food recipe for people who live outside Japan",
    version = "1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    categories = crud.get_table_category(db=db, scale="large")    # categories (categories.scale, categories.categoryId, categories.categoryName, categories.categoryImage_pass)
    return templates.TemplateResponse("index.html", {"request": request, "categories": categories} )

@app.get("/large", response_class=HTMLResponse)
async def read_large(request: Request, large_categoryId: int, db: Session = Depends(get_db)):
    rankingRecipe = crud.get_table_ranking(db=db, categoryId=large_categoryId, scale="large")   # rankingRecipe (rankingRecipe.recipeId, rankingRecipe.categoryId, rankingRecipe.scale, rankingRecipe.categoryName, rankingRecipe.recipeTitle, rankingRecipe.recipeDescription, rankingRecipe.recipeImage_pass)
<<<<<<< HEAD
    #print(rankingRecipe)
    #categoryName = rankingRecipe[0].categoryName
=======
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf
    return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe})


@app.get("/medium", response_class=HTMLResponse)
def read_medium(request: Request, medium_categoryId: Optional[int] = None, db: Session = Depends(get_db)):
    if medium_categoryId == None:
        categories = crud.get_table_category(db=db, scale="medium")    # categories (categories.scale, categories.categoryId, categories.categoryName, categories.categoryImage_pass)
        return templates.TemplateResponse("medium.html", {"request": request, "mediumCategories": categories})
    else:
        rankingRecipe = crud.get_table_ranking(db=db, categoryId=medium_categoryId, scale="medium")    # rankingRecipe (rankingRecipe.recipeId, rankingRecipe.categoryId, rankingRecipe.scale, rankingRecipe.categoryName, rankingRecipe.recipeTitle, rankingRecipe.recipeDescription, rankingRecipe.recipeImage_pass)
<<<<<<< HEAD
        categoryName = rankingRecipe[0].categoryName
        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe, "categoryName": categoryName})
=======
        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe})

>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf


@app.get("/small", response_class=HTMLResponse)
async def read_small(request: Request, small_categoryId: Optional[int] = None, db: Session = Depends(get_db)):
    if not small_categoryId:
        categories = crud.get_table_category(db=db, scale="small")    # categories (categories.scale, categories.categoryId, categories.categoryName, categories.categoryImage_pass)
        return templates.TemplateResponse("small.html", {"request": request, "smallCategories": categories})    
    else:
        rankingRecipe = crud.get_table_ranking(db=db, categoryId=small_categoryId, scale="small")    # rankingRecipe (rankingRecipe.recipeId, rankingRecipe.categoryId, rankingRecipe.scale, rankingRecipe.categoryName, rankingRecipe.recipeTitle, rankingRecipe.recipeDescription, rankingRecipe.recipeImage_pass)
<<<<<<< HEAD
        categoryName = rankingRecipe[0].categoryName
        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe, "categoryName": categoryName})


@app.get("/{scale}/{categoryId}/recipe", response_class=HTMLResponse)
async def recipe(request: Request, scale: str, categoryId: int, recipeId: int, db: Session = Depends(get_db)):
    recipes = crud.get_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId)   # recipes.recipeId, recipes.scale, recipes.categoryId, recipes.recipeTitle, recipes.recipeMaterials, recipes.recipeInstructions, recipes.recipeImage_pass
    recipes = recipes[0]
=======
        return templates.TemplateResponse("ranking.html", {"request": request, "rankingRecipe": rankingRecipe})


@app.get("/recipe", response_class=HTMLResponse)
async def recipe(request: Request, recipeId: int):
    url = f'https://recipe.rakuten.co.jp/recipe/{recipeId}/'
    res = requests.get(url)
    
    soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf

    recipeMaterials = {}
    recipeInstructions = []
    recipeTitle = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": recipes.recipeTitle, }, )
    recipeTitle = recipeTitle.json()["translations"][0]["text"]

<<<<<<< HEAD
    for item, serving in recipes.recipeMaterials.items():
        items = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": item, }, )
        items = items.json()["translations"][0]["text"]
        servings = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": serving, }, )
        servings = servings.json()["translations"][0]["text"]
        recipeMaterials[items] = servings
=======
    for item, serving in zip(items, servings):
        #item_api = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": item.text.replace('\n', ''), }, )
        #item_translated = item_api.json()["translations"][0]["text"]
        #serving_api = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": serving.text.replace('\n', ''), }, )
        #serving_translated = serving_api.json()["translations"][0]["text"]
        material = item.text.replace('\n', '')
        serving = serving.text.replace('\n', '')

        materials[material] = serving

    description = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_howto.section_border_top.section_padding_top.mt32.mb21 > ol > li > span.recipe_howto__text")
    descriptions = {}

    for index, item_description in enumerate(description):
        #description_api = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": item_description.text.replace('\n', ''), }, )
        #description_translated = description_api.json()["translations"][0]["text"]
        description = item_description.text.replace('\n', '')
        descriptions[index+1] = description
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf
    
    for instruction in recipes.recipeInstructions.values():
        instructions = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": instruction, }, )
        instructions = instructions.json()["translations"][0]["text"]
        recipeInstructions.append(instructions)

<<<<<<< HEAD
    
    return templates.TemplateResponse("recipe.html", {"request": request, "recipes": recipes, "recipeTitle": recipeTitle, "recipeMaterials": recipeMaterials, "recipeInstructions": recipeInstructions})
=======
    recipeName_soup = soup.select("#recipeDetailTitle > h1")
    recipeName = recipeName_soup[0].text.split(' ')[0]
    #recipeName_api = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": recipeName, }, )
    #recipeName = recipeName_api.json()["translations"][0]["text"]

    return templates.TemplateResponse("recipe.html", {"request": request, "materials": materials, "descriptions": descriptions, "imageUrl": imageUrl, "recipeName": recipeName},)
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf


@app.get("/register-login", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request,} )
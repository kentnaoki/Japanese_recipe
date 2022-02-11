import requests
from images import MediumCategory
import models
import crud
import time
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form, Depends, HTTPException, status
from bs4 import BeautifulSoup
import glob


url_category = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1082013691690447331"
api_category = requests.get(url_category).json()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_category_db(db: Session = Depends(get_db)):
    scales = ["large", "medium", "small"]
    for scale in scales:
        for category_json in api_category["result"][f"{scale}"]:
            translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": category_json["categoryName"], }, )
            categoryName = translate_api.json()["translations"][0]["text"]
            categoryId = int(category_json["categoryId"])
            categoryImage_pass = f'/images/category/images_{scale}/{categoryId}.jpg'
            print(categoryName, categoryId, categoryImage_pass)

            db = SessionLocal()

            crud.create_table_category(db=db, scale=f"{scale}", categoryName=categoryName, categoryId=categoryId, categoryImage_pass=categoryImage_pass)
        

    print("finish")

def update_category_db():
    scales = ["large", "medium", "small"]
    for scale in scales:
        for category_json in api_category["result"][f"{scale}"]:
            translate_api = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": category_json["categoryName"], }, )
            categoryName = translate_api.json()["translations"][0]["text"]
            categoryId = int(category_json["categoryId"])
            categoryImage_pass = f'/images/category/images_{scale}/{categoryId}.jpg'
            print(categoryId, categoryImage_pass)
            db = SessionLocal()
            crud.update_table_category(db=db, scale=scale, categoryId=categoryId, categoryName=categoryName, categoryImage_pass=categoryImage_pass)

def create_ranking_db(db: Session = Depends(get_db)):
    scales = ["small"] #["large", "medium", "small"]
    # loop through scales of categories
    for scale in scales:

        # loop through categories in API
        for category_json in api_category["result"][f"{scale}"]:

            if scale == "large":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)

            elif scale == "medium":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                medium_categoryId = int((url.split('/')[-2]).split('-')[1])
                
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}-{medium_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)


            elif scale == "small":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                medium_categoryId = int((url.split('/')[-2]).split('-')[1])
                small_categoryId = int((url.split('/')[-2]).split('-')[2])
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}-{medium_categoryId}-{small_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)
            
            for rec in Json_result:
                if scale == "large":
                    categoryId = large_categoryId
                elif scale == "medium":
                    categoryId = medium_categoryId
                elif scale == "small":
                    categoryId = small_categoryId
                recipeId = int(rec["recipeId"])
                db = SessionLocal()
                isDataInDb = crud.check_table_ranking(db=db, recipeId=recipeId, categoryId=categoryId, scale=scale)
                if isDataInDb == True:
                    print(recipeId, categoryId, scale, "exist")
                elif isDataInDb == False:
                    translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
                    recipeTitle = translate_api_title.json()["translations"][0]["text"] 
                    translate_api_description = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
                    recipeDescription = translate_api_description.json()["translations"][0]["text"]
                    translate_api_categoryName = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": categoryName, }, )
                    categoryName = translate_api_categoryName.json()["translations"][0]["text"]

                
                    recipeImage_pass = f'/images/ranking/{scale}/{categoryId}/{recipeId}.jpg'
                    
                    print(recipeId, categoryId, scale, categoryName, recipeImage_pass)
                    crud.create_table_ranking(db=db, recipeId=recipeId, categoryId=categoryId, scale=scale, categoryName=categoryName, recipeTitle=recipeTitle, recipeDescription=recipeDescription, recipeImage_pass=recipeImage_pass)
                else:
                    print("Unexpected error")
    print("finish")

def update_ranking_db(db: Session = Depends(get_db)):
    scales = ["small"]
    # iterate scales of categories
    for scale in scales:

        # iterate categories in API
        for category_json in api_category["result"][f"{scale}"]:

            if scale == "large":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)

            elif scale == "medium":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                medium_categoryId = int((url.split('/')[-2]).split('-')[1])
                
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}-{medium_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)


            elif scale == "small":
                # get the Json result of the ranking from API
                url = category_json["categoryUrl"]
                categoryName = category_json["categoryName"]
                large_categoryId = int((url.split('/')[-2]).split('-')[0])
                medium_categoryId = int((url.split('/')[-2]).split('-')[1])
                small_categoryId = int((url.split('/')[-2]).split('-')[2])
                while True:
                    try: # to avoid error
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={large_categoryId}-{medium_categoryId}-{small_categoryId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()
                        Json_result = rankingUrl_Json["result"]
                        break
                    except KeyError: # if KeyError occurred, request the API again
                        print("Error Occurred")
                        time.sleep(1)
            
            for rec in Json_result:
                if scale == "large":
                    categoryId = large_categoryId
                elif scale == "medium":
                    categoryId = medium_categoryId
                elif scale == "small":
                    categoryId = small_categoryId
                recipeId = int(rec["recipeId"])
                db = SessionLocal()
                '''translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
                recipeTitle = translate_api_title.json()["translations"][0]["text"] 
                translate_api_description = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
                recipeDescription = translate_api_description.json()["translations"][0]["text"]
                translate_api_categoryName = translate_api_title = requests.get("https://api-free.deepl.com/v2/translate", params={"auth_key": "25a0ba9f-e4c2-079a-ca42-6d7f1fce49e5:fx", "source_lang": "JA", "target_lang": "EN-GB", "text": categoryName, }, )
                categoryName = translate_api_categoryName.json()["translations"][0]["text"]'''

            
                recipeImage_pass = f'/images/ranking/{scale}/{categoryId}/{recipeId}.jpg'
                
                isAlreadyInDatabase = crud.check_table_ranking(db=db, recipeId=recipeId, categoryId=categoryId, scale=scale)
                if isAlreadyInDatabase == True:
                    print(recipeId, categoryId, scale, categoryName, recipeImage_pass, "update")
                    #crud.update_table_ranking(db=db, recipeId=recipeId, categoryId=categoryId, categoryName=categoryName, recipeTitle=recipeTitle, recipeDescription=recipeDescription, scale=scale, recipeImage_pass=recipeImage_pass)
                elif isAlreadyInDatabase == False:
                    print(recipeId, categoryId, scale, categoryName, recipeImage_pass, "create")
                    translate_api_title = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeTitle"], }, )
                    recipeTitle = translate_api_title.json()["translations"][0]["text"] 
                    translate_api_description = translate_api_title = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": rec["recipeDescription"], }, )
                    recipeDescription = translate_api_description.json()["translations"][0]["text"]
                    translate_api_categoryName = translate_api_title = requests.get("https://api.deepl.com/v2/translate", params={"auth_key": "eca69a9d-114a-85b0-7684-55ff284e0389", "source_lang": "JA", "target_lang": "EN-GB", "text": categoryName, }, )
                    categoryName = translate_api_categoryName.json()["translations"][0]["text"]
                    crud.create_table_ranking(db=db, recipeId=recipeId, categoryId=categoryId, scale=scale, categoryName=categoryName, recipeTitle=recipeTitle, recipeDescription=recipeDescription, recipeImage_pass=recipeImage_pass)

    print("finish")

def create_recipe_db(db: Session = Depends(get_db)):
    scales = ["large", "medium", "small"]
    for scale in scales:
        path = f'./images/recipe/{scale}/*/*'
        files = glob.glob(path)

        for file in files:
            categoryId = file.split("/")[-2]
            recipeId = file.split("/")[-1].split(".")[0]
        
            db = SessionLocal()
            isDataInDatabase = crud.get_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId)
            
            if len(isDataInDatabase) > 0:
                #crud.update_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId, recipeTitle=recipeTitle, recipeMaterials=recipeMaterials, recipeInstructions=recipeInstructions, recipeImage_pass=recipeImage_pass)
                print(recipeId, scale, "update")
            
            else:
                url = f'https://recipe.rakuten.co.jp/recipe/{recipeId}/'
                res = requests.get(url)
                
                soup = BeautifulSoup(res.content, "html.parser", from_encoding='utf-8')
                
                # make dictionary of materials
                items = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_name")
                servings = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_serving")
                recipeMaterials = {}

                for item, serving in zip(items, servings):
                    material = item.text.replace('\n', '')
                    serving = serving.text.replace('\n', '')

                    recipeMaterials[material] = serving
                instructions = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_howto.section_border_top.section_padding_top.mt32.mb21 > ol > li > span.recipe_howto__text")
                recipeInstructions = {}

                for index, item_instructions in enumerate(instructions):
                    instructions = item_instructions.text.replace('\n', '')
                    recipeInstructions[index+1] = instructions
                
                recipeImage_pass = f'./images/recipe/{scale}/{categoryId}/{recipeId}.jpg'

                recipeTitle_soup = soup.select("#recipeDetailTitle > h1")
                recipeTitle = recipeTitle_soup[0].text.split(' ')[0]

                
                crud.create_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId, recipeTitle=recipeTitle, recipeMaterials=recipeMaterials, recipeInstructions=recipeInstructions, recipeImage_pass=recipeImage_pass)
                print(recipeId, scale, "create")
    print("finish")

def update_recipe_db(db: Session = Depends(get_db)):
    scales = ["large", "medium", "small"]
    for scale in scales:
        path = f'./images/recipe/{scale}/*/*'
        files = glob.glob(path)

        for file in files:
            categoryId = file.split("/")[-2]
            recipeId = file.split("/")[-1].split(".")[0]
            db = SessionLocal()

            isDataInDatabase = crud.get_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId)
            
            if len(isDataInDatabase) > 0:
                recipeImage_pass = f'./images/recipe/{scale}/{categoryId}/{recipeId}.jpg'
                crud.update_table_recipe(db=db, recipeId=recipeId, scale=scale, categoryId=categoryId, recipeImage_pass=recipeImage_pass)
                print(recipeId, scale, recipeImage_pass, "updated")
            else:
                pass

update_ranking_db()

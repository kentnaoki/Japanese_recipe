from re import T
import time
import requests
import json
import os
import glob
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
from bs4 import BeautifulSoup

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Category:
    def __init__(self, categoryId):
        self.categoryId = categoryId

    def add_imageUrl(self, imageUrl):
        self.imageUrl = imageUrl

class MediumCategory:
    def __init__(self, categoryId, mediumCategoryId):
        self.categoryId = categoryId
        self.mediumCategoryId = mediumCategoryId

    def add_mediumImageUrl(self, mediumImageUrl):
        self.mediumImageUrl = mediumImageUrl

class SmallCategory:
    def __init__(self, categoryId, mediumCategoryId, smallCategoryId):
        self.categoryId = categoryId
        self.mediumCategoryId = mediumCategoryId
        self.smallCategoryId = smallCategoryId

    def add_smallImageUrl(self, smallImageUrl):
        self.smallImageUrl = smallImageUrl

img_largeCategory = []

url_category = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1082013691690447331"
api_category = requests.get(url_category).json()

#@app.post("/images/large/", response_model=schemas.Image)
def get_images_largeCategory(db: Session = Depends(get_db)):
    for category_json in api_category["result"]["large"]:
        largeUrl = category_json["categoryUrl"]
        id = int((largeUrl.split('/')[-2]).split('-')[0])
        category = Category(id)
        time.sleep(1)
        while True:
            try:
                rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}"
                imageUrl = requests.get(rankingUrl_Json).json()["result"][0]["mediumImageUrl"]
                break
            except KeyError:
                print("Error Occurred")
        category.add_imageUrl(imageUrl)
        response = requests.get(imageUrl)
        image = response.content

        with open(f'./images/category/images_large/{id}.jpg', 'wb') as img:
            img.write(image)

        '''f = open(f'./images/category/images_large/{id}.txt', 'w')
        f.write(category.imageUrl)
        f.close()'''

    print("finish getting images for large category")

def get_images_mediumCategory():
    for medium_category_json in api_category["result"]["medium"]:
        mediumUrl = medium_category_json["categoryUrl"]
        id = int((mediumUrl.split('/')[-2]).split('-')[0])
        mediumId = int((mediumUrl.split('/')[-2]).split('-')[1])
        mediumCategory = MediumCategory(id, mediumId)
        image_file = f'{mediumId}.jpg'
        # delete this condition when updating
        if os.path.exists(f'./images/category/images_medium/{image_file}'):
            print(id, mediumId)
        else:
            print(mediumId)
            while True:
                try:
                    mediumRankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{mediumId}"
                    mediumImageUrl = requests.get(mediumRankingUrl_Json).json()["result"][0]["mediumImageUrl"]
                    break
                except KeyError:
                    print("Error Occurred")
                    time.sleep(1)
            mediumCategory.add_mediumImageUrl(mediumImageUrl)
            response = requests.get(mediumImageUrl)
            image = response.content

            with open(f'./images/category/images_medium/{mediumId}.jpg', 'wb') as img:
                img.write(image)
            '''f = open(f'./images/category/images_medium/{mediumId}.txt', 'w')
            f.write(mediumCategory.mediumImageUrl)
            f.close()'''
    print("finish getting images for medium category")

def get_images_smallCategory():
    for small_category_json in api_category["result"]["small"]:
        smallUrl = small_category_json["categoryUrl"]
        id = int((smallUrl.split('/')[-2]).split('-')[0])
        mediumId = int((smallUrl.split('/')[-2]).split('-')[1])
        smallId = int((smallUrl.split('/')[-2]).split('-')[2])
        smallCategory = SmallCategory(id, mediumId, smallId)
        text_file = f'{smallId}.jpg'
        # delete this condition when updating
        if os.path.exists(f'./images/category/images_small/{text_file}'):
            print(id, mediumId, smallId)

        else:
            print(smallId)
            while True:
                try:
                    smallRankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{mediumId}-{smallId}"
                    smallImageUrl = requests.get(smallRankingUrl_Json).json()["result"][0]["mediumImageUrl"]
                    break
                except KeyError:
                    print("Error Occurred")
                    time.sleep(1)
            smallCategory.add_smallImageUrl(smallImageUrl)
            response = requests.get(smallImageUrl)
            image = response.content
            with open(f'./images/category/images_small/{smallId}.jpg', 'wb') as img:
                img.write(image)
            '''f = open(f'./images/category/images_small/{smallId}.txt', 'w')
            f.write(smallCategory.smallImageUrl)
            f.close()'''
    print("finish getting images for small category")

def get_images_ranking():
    scales = ["small"]
    #scales = ["large", "medium", "small"]
    # category loop (condition by scale)
    for scale in scales:
        path = f'./images/ranking/{scale}'
        for json_category in api_category["result"][f"{scale}"]:
            url = json_category["categoryUrl"]
            if scale == "large":
                largeId = int((url.split('/')[-2]).split('-')[0])
                while True:
                    try:
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={largeId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()["result"]
                        break
                    except KeyError:
                        print("Error Occurred")
                        time.sleep(1)
                try:
                    os.mkdir(f'{path}/{largeId}')
                except:
                    pass
                for rank in rankingUrl_Json:
                    recipeId = rank['recipeId']
                    if os.path.exists(f'./images/ranking/large/{largeId}/{recipeId}.jpg'):
                        print(largeId, recipeId, "exist")
                    else:
                        imageUrl = rank['mediumImageUrl']
                        response = requests.get(imageUrl)
                        image = response.content
                        with open(f'./images/ranking/large/{largeId}/{recipeId}.jpg', 'wb') as img:
                            img.write(image)
                        print(largeId, recipeId)
                    

            elif scale == "medium":
                largeId = int((url.split('/')[-2]).split('-')[0])
                mediumId = int((url.split('/')[-2]).split('-')[1])
                while True:
                    try:
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={largeId}-{mediumId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()["result"]
                        break
                    except KeyError:
                        print("Error Occurred")
                        time.sleep(1)
                try:
                    os.mkdir(f'{path}/{mediumId}')
                except:
                    pass
                for rank in rankingUrl_Json:
                    recipeId = rank['recipeId']
                    if os.path.exists(f'./images/ranking/medium/{mediumId}/{recipeId}.jpg'):
                        print(mediumId, recipeId, "exist")
                    else:
                        imageUrl = rank['mediumImageUrl']
                        response = requests.get(imageUrl)
                        image = response.content
                        with open(f'./images/ranking/medium/{mediumId}/{recipeId}.jpg', 'wb') as img:
                            img.write(image)
                        print(mediumId, recipeId)
                        
            elif scale == "small":
                largeId = int((url.split('/')[-2]).split('-')[0])
                mediumId = int((url.split('/')[-2]).split('-')[1])
                smallId = int((url.split('/')[-2]).split('-')[2])
                
                while True:
                    try:
                        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={largeId}-{mediumId}-{smallId}"
                        rankingUrl_Json = requests.get(rankingUrl_Json).json()["result"]
                        break
                    except KeyError:
                        print("Error Occurred")
                        time.sleep(1)

                try:
                    os.mkdir(f'{path}/{smallId}')
                except:
                    pass
                for rank in rankingUrl_Json:
                    recipeId = rank['recipeId']
                    if os.path.exists(f'./images/ranking/small/{smallId}/{recipeId}.jpg'):
                        print(smallId, recipeId, "exist")
                    else:
                        imageUrl = rank['mediumImageUrl']
                        response = requests.get(imageUrl)
                        image = response.content
                        with open(f'./images/ranking/small/{smallId}/{recipeId}.jpg', 'wb') as img:
                            img.write(image)
                        print(smallId, recipeId)
    print("finish")

def get_images_recipe():
    scales = ["large", "medium", "small"]
    
    for scale in scales:
        path_recipe = f'./images/recipe/{scale}'
        ranking_path = f'./images/ranking/{scale}/*/*'
        dir = glob.iglob(ranking_path)
        for file in dir:
            if scale == "large":
                largeId = int(file.split("/")[-2])
                recipeId = int(file.split("/")[-1].split(".")[0])
                try:
                    os.mkdir(f'{path_recipe}/{largeId}')
                except:
                    pass
                if os.path.exists(f'./images/recipe/large/{largeId}/{recipeId}.jpg'):
                    print(largeId, recipeId, "exist")
                else:
                    url = f'https://recipe.rakuten.co.jp/recipe/{recipeId}/'
                    res = requests.get(url)
                    
                    soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')
                    image = soup.select("#recipeBasic > div.recipe_info_img > img[src]")
                    for i in image:
                        imageUrl = i.get("src")
                    response = requests.get(imageUrl)
                    image = response.content
                    with open(f'./images/recipe/large/{largeId}/{recipeId}.jpg', 'wb') as img:
                        img.write(image)
                    print(scale, largeId, recipeId)

            elif scale == "medium":
                mediumId = int(file.split("/")[-2])
                recipeId = int(file.split("/")[-1].split(".")[0])
                try:
                    os.mkdir(f'{path_recipe}/{mediumId}')
                except:
                    pass
                if os.path.exists(f'./images/recipe/medium/{mediumId}/{recipeId}.jpg'):
                    print(mediumId, recipeId, "exist")
                else:
                    url = f'https://recipe.rakuten.co.jp/recipe/{recipeId}/'
                    res = requests.get(url)
                    
                    soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')
                    image = soup.select("#recipeBasic > div.recipe_info_img > img[src]")
                    for i in image:
                        imageUrl = i.get("src")
                    response = requests.get(imageUrl)
                    image = response.content
                    with open(f'./images/recipe/medium/{mediumId}/{recipeId}.jpg', 'wb') as img:
                        img.write(image)
                    print(scale, mediumId, recipeId)
            elif scale == "small":
                smallId = int(file.split("/")[-2])
                recipeId = int(file.split("/")[-1].split(".")[0])
                try:
                    os.mkdir(f'{path_recipe}/{smallId}')
                except:
                    pass
                if os.path.exists(f'./images/recipe/small/{smallId}/{recipeId}.jpg') or recipeId == 1370000037:
                    print(smallId, recipeId, "exist")
                else:
                    url = f'https://recipe.rakuten.co.jp/recipe/{recipeId}/'
                    res = requests.get(url)
                    
                    soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')
                    image = soup.select("#recipeBasic > div.recipe_info_img > img[src]")
                    for i in image:
                        imageUrl = i.get("src")
                    response = requests.get(imageUrl)
                    image = response.content
                    with open(f'./images/recipe/small/{smallId}/{recipeId}.jpg', 'wb') as img:
                        img.write(image)
                    print(scale, smallId, recipeId)


if __name__ == "__main__":
    #get_images_largeCategory()
    #get_images_mediumCategory()
    #get_images_smallCategory()
    
    #get_images_ranking()
    get_images_recipe()

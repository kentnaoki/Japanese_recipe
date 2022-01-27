from cgitb import small
import time
import requests
import json
import os

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

def get_images_largeCategory():
    for category_json in api_category["result"]["large"]:
        largeUrl = category_json["categoryUrl"]
        id = int((largeUrl.split('/')[-2]).split('-')[0])
        category = Category(id)
        time.sleep(1)
        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}"
        imageUrl = requests.get(rankingUrl_Json).json()["result"][0]["mediumImageUrl"]
        category.add_imageUrl(imageUrl)

        response = requests.get(imageUrl)
        image = response.content
        with open(f'./images/images_large/{id}.jpg', 'wb') as img:
            img.write(image)

        '''f = open(f'./images/images_large/{id}.txt', 'w')
        f.write(category.imageUrl)
        f.close()'''
    print("finish getting images for small category")

def get_images_mediumCategory():
    for medium_category_json in api_category["result"]["medium"]:
        mediumUrl = medium_category_json["categoryUrl"]
        id = int((mediumUrl.split('/')[-2]).split('-')[0])
        mediumId = int((mediumUrl.split('/')[-2]).split('-')[1])
        mediumCategory = MediumCategory(id, mediumId)
        image_file = f'{mediumId}.jpg'
        # delete this condition when updating
        if os.path.exists(f'./images/images_medium/{image_file}'):
            print(id, mediumId)
        else:
            print(mediumId)
            time.sleep(1)
            mediumRankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{mediumId}"
            mediumImageUrl = requests.get(mediumRankingUrl_Json).json()["result"][0]["mediumImageUrl"]
            mediumCategory.add_mediumImageUrl(mediumImageUrl)
            response = requests.get(mediumImageUrl)
            image = response.content

            with open(f'./images/images_medium/{mediumId}.jpg', 'wb') as img:
                img.write(image)
            '''f = open(f'./images/images_medium/{mediumId}.txt', 'w')
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
        if os.path.exists(f'./images/images_small/{text_file}'):
            print(id, mediumId, smallId)

        else:
            print(smallId)
            time.sleep(1)
            smallRankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}-{mediumId}-{smallId}"
            smallImageUrl = requests.get(smallRankingUrl_Json).json()["result"][0]["mediumImageUrl"]
            smallCategory.add_smallImageUrl(smallImageUrl)
            response = requests.get(smallImageUrl)
            image = response.content
            with open(f'./images/images_small/{smallId}.jpg', 'wb') as img:
                img.write(image)
            '''f = open(f'./images/images_small/{smallId}.txt', 'w')
            f.write(smallCategory.smallImageUrl)
            f.close()'''
    print("finish getting images for small category")


if __name__ == "__main__":
    #get_images_largeCategory()
    #get_images_mediumCategory()
    get_images_smallCategory()
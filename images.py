import time
import requests
import json

class Category:
        def __init__(self, categoryName, categoryId):
            self.categoryName = categoryName
            self.categoryId = categoryId

        def add_imageUrl(self, imageUrl):
            self.imageUrl = imageUrl

class Recipe:
        def __init__(self, foodImageUrl, recipeId, recipeIndication, recipeTitle, recipeUrl, recipeDescription):
            self.foodImageUrl = foodImageUrl
            self.recipeId = recipeId
            self.recipeIndication = recipeIndication
            self.recipeTitle = recipeTitle
            self.recipeUrl = recipeUrl
            self.recipeDescription = recipeDescription

        def add_recipe(self):
            Recipe.recipe_list.append(self)

img_largeCategory = []

url_category = "https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1082013691690447331"
api_category = requests.get(url_category).json()

def get_images_largeCategory():
    for index, category_json in enumerate(api_category["result"]["large"]):
        category = Category(category_json["categoryName"], category_json["categoryId"])
        id = category.categoryId
        rankingUrl_Json = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1082013691690447331&categoryId={id}"
        imageUrl = requests.get(rankingUrl_Json).json()['result'][0]['mediumImageUrl']
        category.add_imageUrl(imageUrl)
        f = open(f'./images/images_large/{category.categoryId}.txt', 'w')
        f.write(category.imageUrl)
        f.close()
        time.sleep(1)

if __name__ == "__main__":
    get_images_largeCategory()

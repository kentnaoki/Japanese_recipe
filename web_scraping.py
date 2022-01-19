import requests
from bs4 import BeautifulSoup

url = 'https://recipe.rakuten.co.jp/recipe/1450019309/'
res = requests.get(url)

soup = BeautifulSoup(res.text, "html.parser", from_encoding='utf-8')

'''
items = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_name")
servings = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_material.mb32 > ul > li > .recipe_material__item_serving")
materials = {}

for item, serving in zip(items, servings):
    materials[item.text.replace('\n', '')] = serving.text.replace('\n', '')

print(materials)'''

'''description = soup.select("#recipeDetail > div.recipe_detail.side_margin > section.recipe_howto.section_border_top.section_padding_top.mt32.mb21 > ol > li > span.recipe_howto__text")
descriptions = {}

for index, item in enumerate(description):
    descriptions[index+1] = item.text.replace('\n', '')

print(descriptions)'''

description = soup.select("#recipeBasic > div.recipe_info_img > img[src]")

for i in description:
    url = i.get("src")


#descriptions.append()
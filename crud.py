import string
from tokenize import String
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import update, delete, insert, exc, and_
import sqlite3


def get_image_large(db: Session, scale: str, image_number: int):
    return db.query(models.Image).filter(models.Image.image_number == image_number)

def create_table_recipe(db: Session, recipeId: int, scale: str, categoryName: str, title: str, materials: str, instructions: str, image_pass: str):
    db_recipe = models.RecipeTable(recipeId=recipeId, scale=scale, categoryName=categoryName, title=title, materials=materials, instructions=instructions, image_pass=image_pass)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

def create_table_category(db: Session, scale: str, categoryName: str, categoryId: int, categoryImage_pass: str):
    db_category = models.CategoryTable(scale=scale, categoryName=categoryName, categoryId=categoryId, categoryImage_pass=categoryImage_pass)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

def update_table_category(db: Session, scale: str, categoryId: int, categoryImage_pass: str):
    query = db.query(models.CategoryTable)
    db_category_update = query.filter(models.CategoryTable.scale == scale, models.CategoryTable.categoryId == categoryId).first()
    db_category_update.categoryImage_pass = categoryImage_pass
    db.commit()

def get_table_category(db: Session, scale: str):
    db_category_data = db.query(models.CategoryTable).filter(models.CategoryTable.scale == scale).all()
    return db_category_data

def check_table_ranking(db: Session, recipeId: int, categoryId: int, scale: str):
    if len(db.query(models.RankingTable).filter(models.RankingTable.recipeId == recipeId, models.RankingTable.categoryId == categoryId, models.RankingTable.scale == scale).all())  > 0:
        return True
    elif len(db.query(models.RankingTable).filter(models.RankingTable.recipeId == recipeId, models.RankingTable.categoryId == categoryId, models.RankingTable.scale == scale).all()) == 0:
        return False
    else:
        print("Error")

def create_table_ranking(db: Session, recipeId: int, categoryId: int, scale: str, categoryName: str, recipeTitle: str, recipeDescription: str, recipeImage_pass: str):
    db_ranking = models.RankingTable(recipeId=recipeId, categoryId=categoryId, scale=scale, categoryName=categoryName, recipeTitle=recipeTitle, recipeDescription=recipeDescription, recipeImage_pass=recipeImage_pass)
    db.add(db_ranking)
    db.commit()
    db.refresh(db_ranking)
        
def update_table_ranking(db: Session, recipeId: int, categoryId: int, scale: str, categoryName: str, recipeTitle: str, recipeDescription: str, recipeImage_pass: str):
    try:
        query = db.query(models.RankingTable)
        db_ranking_update = query.filter(models.RankingTable.recipeId == recipeId, models.RankingTable.categoryId == categoryId, models.RankingTable.scale == scale).first()
        db_ranking_update.categoryName = categoryName
        db_ranking_update.recipeTitle = recipeTitle
        db_ranking_update.recipeDescription = recipeDescription
        db_ranking_update.recipeImage_pass = recipeImage_pass
        db.commit()
    except:
        db_ranking = models.RankingTable(recipeId=recipeId, categoryId=categoryId, scale=scale, categoryName=categoryName, recipeTitle=recipeTitle, recipeDescription=recipeDescription, recipeImage_pass=recipeImage_pass)
        db.add(db_ranking)
        db.commit()
        db.refresh(db_ranking)

def get_table_ranking(db: Session, categoryId: int, scale: str):
    db_ranking_data = db.query(models.RankingTable).filter(models.RankingTable.categoryId == categoryId, models.RankingTable.scale == scale).all()
    return db_ranking_data

def get_table_ranking_recipeTitle(db: Session, categoryId: int, scale: str, recipeId: int):
    db_ranking_data = db.query(models.RankingTable).filter(models.RankingTable.categoryId == categoryId, models.RankingTable.scale == scale, models.RankingTable.recipeId == recipeId).all()
    return db_ranking_data

def create_table_recipe(db: Session, recipeId: int, scale: str, categoryId: int, recipeTitle: str, recipeMaterials: dict, recipeInstructions: dict, recipeImage_pass: str):
    db_recipe = models.RecipeTable(recipeId=recipeId, scale=scale, categoryId=categoryId, recipeTitle=recipeTitle, recipeMaterials=recipeMaterials, recipeInstructions=recipeInstructions, recipeImage_pass=recipeImage_pass)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

def update_table_recipe(db: Session, recipeId: int, scale: str, categoryId: int, recipeImage_pass: str):
    query = db.query(models.RecipeTable)
    db_recipe_update = query.filter(models.RecipeTable.recipeId == recipeId, models.RecipeTable.scale == scale, models.RecipeTable.categoryId == categoryId).first()
    db_recipe_update.recipeImage_pass = recipeImage_pass
    db.commit()

def get_table_recipe(db: Session, recipeId: int, scale: str, categoryId: int):
    db_recipe = db.query(models.RecipeTable).filter(models.RecipeTable.recipeId == recipeId, models.RecipeTable.scale == scale, models.RecipeTable.categoryId == categoryId).all()
    return db_recipe

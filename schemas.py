from typing import List, Optional
from pydantic import BaseModel

class Category(BaseModel):
    id: int
    scale: str
    categoryName: str
    categoryId: int
    categoryImage_pass: str

class Ranking(BaseModel):
    id: int
    recipeId: int
    categoryId: int
    scale: str
    categoryName: str
    recipeTitle: str
    recipeDescription: str
    recipeImage_pass: str

class Recipe(BaseModel):
    id: int
    recipeId: int
    scale: str
    recipeTitle: str
    recipeMaterials: str
    recipeInstructions: str
    recipeImage_pass: str
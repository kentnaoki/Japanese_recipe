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
<<<<<<< HEAD
    categoryId: int
    recipeTitle: str
    recipeMaterials: dict
    recipeInstructions: dict
=======
    recipeTitle: str
    recipeMaterials: str
    recipeInstructions: str
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf
    recipeImage_pass: str
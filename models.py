from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import relationship

from database import Base

class CategoryTable(Base):
    __tablename__ = "categories"
    id = Column(Integer, index=True)
    scale = Column(String, index=True, primary_key=True)
    categoryName = Column(String, index=True)
    categoryId = Column(Integer, index=True, primary_key=True)
    categoryImage_pass = Column(String, index=True)

class RankingTable(Base):
    __tablename__ = "rankings"
    id = Column(Integer, index=True)
    recipeId = Column(Integer, index=True, primary_key=True)
    categoryId = Column(Integer, index=True, primary_key=True)
    scale = Column(String, index=True, primary_key=True)
    categoryName = Column(String, index=True)
    recipeTitle = Column(String, index=True)
    recipeDescription = Column(String, index=True)
    recipeImage_pass = Column(String, index=True)

class RecipeTable(Base):
    __tablename__ = "recipes"
    id = Column(Integer, index=True)
    recipeId = Column(Integer, index=True, primary_key=True)
    scale = Column(String, index=True, primary_key=True)
<<<<<<< HEAD
    categoryId = Column(Integer, index=True, primary_key=True)
    recipeTitle = Column(String, index=True)
    recipeMaterials = Column(JSON, index=True)
    recipeInstructions = Column(JSON, index=True)
=======
    recipeTitle = Column(String, index=True)
    recipeMaterials = Column(String, index=True)
    recipeInstructions = Column(String, index=True)
>>>>>>> 4344d5026f46d38d4b1fa1a30d16a639153028cf
    recipeImage_pass = Column(String, index=True)
from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI(
    title = "Japanese food recipe",
    description = "Authentic Japanese food recipe for people who live outside Japan",
    version = "0.9 beta"
)

def index(request: Request):
    return {"Hello", "World"}
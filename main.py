from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from EndPoints.Character_END import router_characters
from EndPoints.Bosses_EDN import router_bosses
from EndPoints.Web_END import router_web
from db import create_all_tables

app = FastAPI(lifespan=create_all_tables)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router_characters)
app.include_router(router_bosses)
app.include_router(router_web)



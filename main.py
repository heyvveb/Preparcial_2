
from fastapi import FastAPI
from EndPoints.Character_END import router_characters
from EndPoints.Bosses_EDN import router_bosses
from db import create_all_tables

app = FastAPI(lifespan=create_all_tables)
app.include_router(router_characters)
app.include_router(router_bosses)



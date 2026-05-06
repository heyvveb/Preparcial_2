from sqlmodel import Session, create_engine, SQLModel
from fastapi import FastAPI, Depends
from typing import Annotated
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
load_dotenv()
sqlite_url= os.getenv("DATABASE_URL")
engine = create_engine(sqlite_url)

@asynccontextmanager
async def create_all_tables(app: FastAPI):
    from Modelos.Character import CharacterID  
    from Modelos.Boss import BossID 
    SQLModel.metadata.create_all(engine)
    yield


def get_session()->Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
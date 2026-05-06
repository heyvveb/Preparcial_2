
from typing import Optional
from sqlmodel import SQLModel, Field
from Modelos.Enums import StatusEnum,main_statEnum

class Character(SQLModel):
    name: str
    level: int = Field(default=1)
    is_hollow: bool = Field(default=False)
    main_stat: Optional[main_statEnum] = None

class CharacterID(Character, table=True):
    id : int | None = Field(default=None, primary_key=True,gt=0)
    status: StatusEnum = Field(default=StatusEnum.active)

class CharacterUpdate(SQLModel):
    name: Optional[str] = None
    level: Optional[int] = None
    is_hollow: Optional[bool] = None
    main_stat: Optional[main_statEnum] = None


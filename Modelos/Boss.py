
from typing import Optional
from sqlmodel import SQLModel, Field
from Modelos.Enums import StatusEnum

class Boss(SQLModel):
    name: str
    health: int
    is_optional: bool = Field(default=False)
    phase_count: int = Field(default=1)

class BossID(Boss, table=True):
    id : int | None = Field(default=None, primary_key=True,gt=0)
    status: StatusEnum = Field(default=StatusEnum.active)

class BossUpdate(SQLModel):
    name: Optional[str] = None
    health: Optional[int] = None
    is_optional: Optional[bool] = None
    phase_count: Optional[int] = None

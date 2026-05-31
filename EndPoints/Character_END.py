from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from typing import List
from Modelos.Character import Character, CharacterID, CharacterUpdate
from Modelos.Enums import main_statEnum
from db import SessionDep
from Operations.Character_OP import *

router_characters = APIRouter(prefix="/Characters", tags=["Characters"])

@router_characters.post("/", response_model=CharacterID)
async def create_character(character: Character, session: SessionDep):
    return create_character_db(character, session)

@router_characters.get("/", response_model=List[CharacterID])
async def get_all_characters(
    session: SessionDep,
    search: str = Query("", description="Filter by name"),
    is_hollow: Optional[bool] = Query(None, description="Filter by hollow status"),
    main_stat: Optional[main_statEnum] = Query(None, description="Filter by main stat"),
    level_min: Optional[int] = Query(None, description="Minimum level"),
    level_max: Optional[int] = Query(None, description="Maximum level"),
):
    return filter_characters_db(session, search=search, is_hollow=is_hollow, main_stat=main_stat, level_min=level_min, level_max=level_max)

@router_characters.get("/deleted", response_model=List[CharacterID])
async def get_all_deleted(session: SessionDep):
    return show_all_deleted_characters_db(session)

@router_characters.get("/{id}", response_model=CharacterID)
async def get_character(id: int, session: SessionDep):
    character = find_one_character_db(id, session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router_characters.put("/{id}", response_model=CharacterID)
async def update_character(id: int, new_character: CharacterUpdate, session: SessionDep):
    character = update_one_character_db(id, new_character, session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found or inactive")
    return character


@router_characters.delete("/{id}", response_model=CharacterID)
async def delete_character(id: int, session: SessionDep):
    character = delete_one_character_db(id, session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found or already inactive")
    return character



@router_characters.patch("/{id}/restore", response_model=CharacterID)
async def restore_character(id: int, session: SessionDep):
    character = restore_one_character_db(id, session)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character
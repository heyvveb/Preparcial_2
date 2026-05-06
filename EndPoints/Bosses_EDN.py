from fastapi import APIRouter, HTTPException
from typing import List
from Modelos.Boss import Boss, BossID, BossUpdate
from db import SessionDep
from Operations.Boss_OP import *

router_bosses = APIRouter(prefix="/Bosses", tags=["Bosses"])

@router_bosses.post("/", response_model=BossID)
async def create_boss(boss: Boss, session: SessionDep):
    return create_boss_db(boss, session)

@router_bosses.get("/", response_model=List[BossID])
async def get_all_bosses(session: SessionDep):
    return show_all_bosses_db(session)

@router_bosses.get("/deleted", response_model=List[BossID])
async def get_all_deleted(session: SessionDep):
    return show_all_deleted_db(session)

@router_bosses.get("/{id}", response_model=BossID)
async def get_boss(id: int, session: SessionDep):
    boss = find_one_boss_db(id, session)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss not found")
    return boss


@router_bosses.put("/{id}", response_model=BossID)
async def update_boss(id: int, new_boss: BossUpdate, session: SessionDep):
    boss = update_one_boss_db(id, new_boss, session)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss not found or inactive")
    return boss


@router_bosses.delete("/{id}", response_model=BossID)
async def delete_boss(id: int, session: SessionDep):
    boss = delete_one_boss_db(id, session)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss not found or already inactive")
    return boss



@router_bosses.patch("/{id}/restore", response_model=BossID)
async def restore_boss(id: int, session: SessionDep):
    boss = restore_one_boss_db(id, session)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss not found")
    return boss
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from db import SessionDep
from Modelos.Boss import Boss, BossID, BossUpdate
from Modelos.Character import Character, CharacterID, CharacterUpdate
from Modelos.Enums import main_statEnum
from Operations.Boss_OP import *
from Operations.Character_OP import *

router_web = APIRouter()
templates = Jinja2Templates(directory="templates")


def validate_boss_form(data: dict) -> dict:
    errors = {}
    name = data.get("name", "").strip()
    if not name:
        errors["name"] = "El nombre es obligatorio."
    health = data.get("health", "").strip()
    if not health:
        errors["health"] = "La salud es obligatoria."
    else:
        try:
            h = int(health)
            if h <= 0:
                errors["health"] = "Debe ser un número positivo."
        except ValueError:
            errors["health"] = "Debe ser un número válido."
    phase_count = data.get("phase_count", "").strip()
    if not phase_count:
        errors["phase_count"] = "La cantidad de fases es obligatoria."
    else:
        try:
            pc = int(phase_count)
            if pc <= 0:
                errors["phase_count"] = "Debe ser un número positivo."
        except ValueError:
            errors["phase_count"] = "Debe ser un número válido."
    return errors


def validate_character_form(data: dict) -> dict:
    errors = {}
    name = data.get("name", "").strip()
    if not name:
        errors["name"] = "El nombre es obligatorio."
    level = data.get("level", "").strip()
    if not level:
        errors["level"] = "El nivel es obligatorio."
    else:
        try:
            lv = int(level)
            if lv <= 0:
                errors["level"] = "Debe ser un número positivo."
        except ValueError:
            errors["level"] = "Debe ser un número válido."
    main_stat = data.get("main_stat", "").strip()
    if main_stat and main_stat not in [e.value for e in main_statEnum]:
        errors["main_stat"] = "Stat principal no válido."
    return errors


@router_web.get("/")
async def index(request: Request, session: SessionDep):
    boss_count = len(show_all_bosses_db(session))
    character_count = len(show_all_characters_db(session))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "boss_count": boss_count,
        "character_count": character_count,
    })


@router_web.get("/bosses/")
async def list_bosses(request: Request, session: SessionDep, search: str = ""):
    if search:
        bosses = search_bosses_by_name_db(search, session)
    else:
        bosses = show_all_bosses_db(session)
    return templates.TemplateResponse("bosses/list.html", {
        "request": request,
        "bosses": bosses,
        "search": search,
    })


@router_web.get("/bosses/create")
async def create_boss_form(request: Request):
    return templates.TemplateResponse("bosses/create.html", {
        "request": request,
        "errors": {},
        "form_data": {},
    })


@router_web.post("/bosses/create")
async def create_boss_submit(request: Request, session: SessionDep):
    data = await request.form()
    form_data = dict(data)
    errors = validate_boss_form(form_data)
    if errors:
        return templates.TemplateResponse("bosses/create.html", {
            "request": request,
            "errors": errors,
            "form_data": form_data,
        }, status_code=422)
    is_optional = form_data.get("is_optional", "false") == "true"
    boss = Boss(
        name=form_data["name"].strip(),
        health=int(form_data["health"]),
        is_optional=is_optional,
        phase_count=int(form_data["phase_count"]),
    )
    create_boss_db(boss, session)
    return RedirectResponse(url="/bosses/", status_code=303)


@router_web.get("/bosses/{id}/edit")
async def edit_boss_form(request: Request, id: int, session: SessionDep):
    boss = find_one_boss_db(id, session)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")
    return templates.TemplateResponse("bosses/edit.html", {
        "request": request,
        "boss": boss,
        "errors": {},
        "form_data": {},
    })


@router_web.post("/bosses/{id}/edit")
async def edit_boss_submit(request: Request, id: int, session: SessionDep):
    boss = find_one_boss_db(id, session)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")
    data = await request.form()
    form_data = dict(data)
    errors = validate_boss_form(form_data)
    if errors:
        return templates.TemplateResponse("bosses/edit.html", {
            "request": request,
            "boss": boss,
            "errors": errors,
            "form_data": form_data,
        }, status_code=422)
    is_optional = form_data.get("is_optional", "false") == "true"
    boss_update = BossUpdate(
        name=form_data["name"].strip(),
        health=int(form_data["health"]),
        is_optional=is_optional,
        phase_count=int(form_data["phase_count"]),
    )
    update_one_boss_db(id, boss_update, session)
    return RedirectResponse(url="/bosses/", status_code=303)


@router_web.post("/bosses/{id}/delete")
async def delete_boss(id: int, session: SessionDep):
    boss = delete_one_boss_db(id, session)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")
    return RedirectResponse(url="/bosses/", status_code=303)


@router_web.post("/bosses/{id}/restore")
async def restore_boss(id: int, session: SessionDep):
    boss = restore_one_boss_db(id, session)
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")
    return RedirectResponse(url="/bosses/", status_code=303)


@router_web.get("/bosses/deleted")
async def list_deleted_bosses(request: Request, session: SessionDep):
    bosses = show_all_deleted_db(session)
    return templates.TemplateResponse("bosses/deleted.html", {
        "request": request,
        "bosses": bosses,
    })


@router_web.get("/characters/")
async def list_characters(request: Request, session: SessionDep, search: str = ""):
    if search:
        characters = search_characters_by_name_db(search, session)
    else:
        characters = show_all_characters_db(session)
    return templates.TemplateResponse("characters/list.html", {
        "request": request,
        "characters": characters,
        "search": search,
    })


@router_web.get("/characters/create")
async def create_character_form(request: Request):
    return templates.TemplateResponse("characters/create.html", {
        "request": request,
        "errors": {},
        "form_data": {},
    })


@router_web.post("/characters/create")
async def create_character_submit(request: Request, session: SessionDep):
    data = await request.form()
    form_data = dict(data)
    form_data["is_hollow"] = "true" if form_data.get("is_hollow") == "true" else "false"
    errors = validate_character_form(form_data)
    if errors:
        return templates.TemplateResponse("characters/create.html", {
            "request": request,
            "errors": errors,
            "form_data": form_data,
        }, status_code=422)
    is_hollow = form_data.get("is_hollow") == "true"
    main_stat = form_data.get("main_stat", "").strip() or None
    character = Character(
        name=form_data["name"].strip(),
        level=int(form_data["level"]),
        is_hollow=is_hollow,
        main_stat=main_stat,
    )
    create_character_db(character, session)
    return RedirectResponse(url="/characters/", status_code=303)


@router_web.get("/characters/{id}/edit")
async def edit_character_form(request: Request, id: int, session: SessionDep):
    character = find_one_character_db(id, session)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return templates.TemplateResponse("characters/edit.html", {
        "request": request,
        "character": character,
        "errors": {},
        "form_data": {},
    })


@router_web.post("/characters/{id}/edit")
async def edit_character_submit(request: Request, id: int, session: SessionDep):
    character = find_one_character_db(id, session)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    data = await request.form()
    form_data = dict(data)
    form_data["is_hollow"] = "true" if form_data.get("is_hollow") == "true" else "false"
    errors = validate_character_form(form_data)
    if errors:
        return templates.TemplateResponse("characters/edit.html", {
            "request": request,
            "character": character,
            "errors": errors,
            "form_data": form_data,
        }, status_code=422)
    is_hollow = form_data.get("is_hollow") == "true"
    main_stat = form_data.get("main_stat", "").strip() or None
    character_update = CharacterUpdate(
        name=form_data["name"].strip(),
        level=int(form_data["level"]),
        is_hollow=is_hollow,
        main_stat=main_stat,
    )
    update_one_character_db(id, character_update, session)
    return RedirectResponse(url="/characters/", status_code=303)


@router_web.post("/characters/{id}/delete")
async def delete_character(id: int, session: SessionDep):
    character = delete_one_character_db(id, session)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return RedirectResponse(url="/characters/", status_code=303)


@router_web.post("/characters/{id}/restore")
async def restore_character(id: int, session: SessionDep):
    character = restore_one_character_db(id, session)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return RedirectResponse(url="/characters/", status_code=303)


@router_web.get("/characters/deleted")
async def list_deleted_characters(request: Request, session: SessionDep):
    characters = show_all_deleted_db(session)
    return templates.TemplateResponse("characters/deleted.html", {
        "request": request,
        "characters": characters,
    })

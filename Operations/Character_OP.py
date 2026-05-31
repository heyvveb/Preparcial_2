from sqlmodel import Session, select

from Modelos.Character import Character, CharacterID, CharacterUpdate

def create_character_db(character: Character, session: Session):
    new_character = CharacterID.model_validate(character)
    session.add(new_character)
    session.commit()
    session.refresh(new_character)

    return new_character

def show_all_characters_db(session: Session):
    statement = select(CharacterID).where(CharacterID.status == "active")
    return session.exec(statement).all()

def show_all_deleted_db(session: Session):
    statement = select(CharacterID).where(CharacterID.status == "inactive")
    return session.exec(statement).all()

def filter_characters_db(session: Session, search: str = "", is_hollow: bool | None = None, main_stat: str | None = None, level_min: int | None = None, level_max: int | None = None):
    statement = select(CharacterID).where(CharacterID.status == "active")
    if search:
        statement = statement.where(CharacterID.name.like(f"%{search}%"))
    if is_hollow is not None:
        statement = statement.where(CharacterID.is_hollow == is_hollow)
    if main_stat:
        statement = statement.where(CharacterID.main_stat == main_stat)
    if level_min is not None:
        statement = statement.where(CharacterID.level >= level_min)
    if level_max is not None:
        statement = statement.where(CharacterID.level <= level_max)
    return session.exec(statement).all()

def find_one_character_db(id: int, session: Session):
    character = session.get(CharacterID, id)
    if not character or character.status != "active":
        return None
    return character

def update_one_character_db(id: int, new_character: CharacterUpdate, session: Session):
    character = find_one_character_db(id, session)
    if character is None:
        return None
    character_data = new_character.model_dump(exclude_unset=True)
    character.sqlmodel_update(character_data)
    session.add(character)
    session.commit()
    session.refresh(character)
    return character

def delete_one_character_db(id: int, session: Session):
    character = session.get(CharacterID, id)
    if not character or character.status == "inactive":
        return None 
    character.status = "inactive"
    session.add(character)
    session.commit()
    session.refresh(character)
    return character

def restore_one_character_db(id: int, session: Session):
    character = session.get(CharacterID, id)
    if not character:
        return None
    character.status = "active"
    session.add(character)
    session.commit()
    session.refresh(character)
    return character

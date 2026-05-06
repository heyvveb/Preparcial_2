from sqlmodel import Session, select

from Modelos.Boss import Boss, BossID, BossUpdate

def create_boss_db(boss: Boss, session: Session):
    new_boss = BossID.model_validate(boss)
    session.add(new_boss)
    session.commit()
    session.refresh(new_boss)
    return new_boss

def show_all_bosses_db(session: Session):
    statement = select(BossID).where(BossID.status == "active")
    return session.exec(statement).all()

def show_all_deleted_db(session: Session):
    statement = select(BossID).where(BossID.status == "inactive")
    return session.exec(statement).all()

def find_one_boss_db(id: int, session: Session):
    boss = session.get(BossID, id)
    if not boss or boss.status != "active":
        return None
    return boss

def update_one_boss_db(id: int, new_boss: BossUpdate, session: Session):
    boss = find_one_boss_db(id, session)
    if boss is None:
        return None
    boss_data = new_boss.model_dump(exclude_unset=True)
    boss.sqlmodel_update(boss_data)
    session.add(boss)
    session.commit()
    session.refresh(boss)
    return boss

def delete_one_boss_db(id: int, session: Session):
    boss = session.get(BossID, id)
    if not boss or boss.status == "inactive":
        return None
    boss.status = "inactive"
    session.add(boss)
    session.commit()
    session.refresh(boss)
    return boss

def restore_one_boss_db(id: int, session: Session):
    boss = session.get(BossID, id)
    if not boss:
        return None
    boss.status = "active"
    session.add(boss)
    session.commit()
    session.refresh(boss)
    return boss

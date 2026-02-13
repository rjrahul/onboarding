from sqlalchemy.orm import Session
from app.schemas.blacklist import BlacklistCreate
from app.crud import blacklist as crud

def create_new_blacklist(db: Session, blacklist_entry: BlacklistCreate):    
    return crud.create_blacklist_entry(db, blacklist_entry)

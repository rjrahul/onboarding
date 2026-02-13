from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.blacklist import BlacklistCreate, Blacklist as BlacklistOut
from app.services import blacklist as service

router = APIRouter(prefix="/blacklist", tags=["Blacklist"])

@router.post("/", response_model=BlacklistOut)
async def create_blacklist_entry(blacklist_entry: BlacklistCreate, db: Session = Depends(get_db)):
    return service.create_new_blacklist(db, blacklist_entry)


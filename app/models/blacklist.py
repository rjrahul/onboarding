from sqlalchemy import Column, Integer, String
from app.core.database import Base

class BlacklistModel(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)

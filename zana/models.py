from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime

from .database import Base

class ZealIdentifier(Base):
    __tablename__ = "zealidentifier"

    zeal = Column(String, primary_key=True, index=True)
    version = Column(Integer, default=0)
    is_assigned = Column(Boolean, default=False)
    assigned_to = Column(String)
    assigned_on = Column(DateTime)
    prefix = Column(String, index=True)
    created_on = Column(DateTime)
    linkage_id = Column(String)
    pool = Column(String)


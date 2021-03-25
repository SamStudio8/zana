from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime

from .database import Base

class ZealIdentifier(Base):
    __tablename__ = "zealidentifier"

    zeal = Column(String, primary_key=True, index=True)
    is_assigned = Column(Boolean, default=False)
    assigned_to = Column(String)
    assigned_on = Column(DateTime)


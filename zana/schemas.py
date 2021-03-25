import datetime

from typing import List, Optional

from pydantic import BaseModel

class ZealIdentifierBase(BaseModel):
    zeal: str
    is_assigned: Optional[bool] = False
    assigned_to: Optional[str] = None
    assigned_on: Optional[datetime.datetime] = None

class ZealIdentifierCreate(ZealIdentifierBase):
    pass

class ZealIdentifier(ZealIdentifierBase):
    class Config:
        orm_mode = True

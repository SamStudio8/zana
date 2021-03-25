import datetime

from typing import List, Optional

from pydantic import BaseModel

class ZealIdentifierBase(BaseModel):
    zeal: str

class ZealIdentifierCreate(ZealIdentifierBase):
    pass

class ZealIdentifier(ZealIdentifierBase):

    assigned_to: Optional[str] = None
    is_assigned: Optional[bool] = False
    assigned_on: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

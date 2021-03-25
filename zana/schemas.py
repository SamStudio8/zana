import datetime

from typing import List, Optional

from pydantic import BaseModel

class ZealIdentifierBase(BaseModel):
    zeal: str
    version: Optional[int] = 0

class ZealIdentifierCreate(ZealIdentifierBase):
    pass

class ZealIdentifier(ZealIdentifierBase):
    assigned_to: Optional[str] = None
    is_assigned: Optional[bool] = False
    assigned_on: Optional[datetime.datetime] = None
    created_on: datetime.datetime

    class Config:
        orm_mode = True

class ZealAssignmentRequest(BaseModel):
    n: int
    org_code: str


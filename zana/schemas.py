import datetime

from typing import List, Optional

from pydantic import BaseModel

class ZealIdentifierBase(BaseModel):
    zeal: str
    pool: str
    version: Optional[int] = 0

class ZealIdentifierCreate(ZealIdentifierBase):
    pass

class ZealIdentifier(ZealIdentifierBase):
    assigned_to: Optional[str] = None
    is_assigned: Optional[bool] = False
    prefix: Optional[str] = None
    assigned_on: Optional[datetime.datetime] = None
    created_on: datetime.datetime
    linkage_id: Optional[str] = None

    class Config:
        orm_mode = True


class ZealLinkageAssignmentRequest(BaseModel):
    org_code: str
    prefix: str
    pool: str
    linkage_id: Optional[str] = None


class ZealPoolSizeRequest(BaseModel):
    pool: str


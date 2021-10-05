from sqlalchemy.orm import Session
from sqlalchemy import func # https://stackoverflow.com/a/4086229/2576437

from datetime import datetime
import time

from . import models, schemas

def create_identifier(db: Session, zeal: schemas.ZealIdentifierCreate):
    zeal_obj = models.ZealIdentifier(**zeal.dict())
    zeal_obj.created_on = datetime.utcnow()
    db.add(zeal_obj)
    db.commit()
    db.refresh(zeal_obj)
    return zeal_obj

def get_identifier(db: Session, zeal: str):
    qs = db.query(models.ZealIdentifier).filter(models.ZealIdentifier.is_assigned == True, models.ZealIdentifier.zeal == zeal)
    return qs.first()

def get_identifier_from_linkage(db: Session, linkage_id: str):
    qs = db.query(models.ZealIdentifier).filter(models.ZealIdentifier.is_assigned == True, models.ZealIdentifier.linkage_id == linkage_id)
    return qs.first()

def get_random_free_zeal(db: Session, pool: str):
    # Use func.random to grab random result https://stackoverflow.com/a/60815
    return db.query(models.ZealIdentifier).filter(models.ZealIdentifier.pool == pool, models.ZealIdentifier.is_assigned == False).order_by(func.random()).first()

def assign_identifier(db: Session, request: schemas.ZealLinkageAssignmentRequest):

    with db.begin():
        zeal = get_random_free_zeal(db, request.pool)
        if zeal:
            zeal.version += 1
            zeal.is_assigned = True
            zeal.linkage_id = request.linkage_id
            zeal.assigned_to = request.org_code
            zeal.prefix = request.prefix
            zeal.assigned_on = datetime.utcnow()
            db.add(zeal)

    return zeal

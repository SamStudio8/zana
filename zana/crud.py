from sqlalchemy.orm import Session
from sqlalchemy import func # https://stackoverflow.com/a/4086229/2576437

from datetime import datetime

from . import models, schemas

def create_identifier(db: Session, zeal: schemas.ZealIdentifierCreate):
    zeal_obj = models.ZealIdentifier(**zeal.dict())
    db.add(zeal_obj)
    db.commit()
    db.refresh(zeal_obj)
    return zeal_obj

def get_identifier(db: Session, zeal: str):
    return db.query(models.ZealIdentifier).filter(models.ZealIdentifier.zeal == zeal).first()

def assign_identifiers(db: Session, request: schemas.ZealAssignmentRequest):
    # TODO Is this safe in parallel?
    # TODO What to do when the pool is exhausted? Currently this will just return however many is left if < n

    zeals = []
    for i in range(request.n):
        zeal = db.query(models.ZealIdentifier).filter(models.ZealIdentifier.is_assigned == False).first()
        if zeal:
            zeal.is_assigned = True
            zeal.assigned_to = request.org_code
            zeal.assigned_on = datetime.utcnow()

            db.add(zeal)
            db.commit()
            db.refresh(zeal)

            zeals.append(zeal)

    return zeals

from sqlalchemy.orm import Session
from sqlalchemy import func # https://stackoverflow.com/a/4086229/2576437

from . import models, schemas

def create_identifier(db: Session, zeal: schemas.ZealIdentifierCreate):
    zeal_obj = models.ZealIdentifier(**zeal.dict())
    db.add(zeal_obj)
    db.commit()
    db.refresh(zeal_obj)
    return zeal_obj

def get_identifier(db: Session, zeal: str):
    return db.query(models.ZealIdentifier).filter(models.ZealIdentifier.zeal == zeal).first()

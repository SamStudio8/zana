from sqlalchemy.orm import Session
from sqlalchemy import func # https://stackoverflow.com/a/4086229/2576437

from datetime import datetime
import fcntl
import os

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

def _open_zeal_lock(zeal_id):
    fl = open('/tmp/%s' % zeal_id, 'w')
    try:
        fcntl.flock(fl, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fl
    except Exception:
        fl.close() # close this handle
        return None

def _close_zeal_lock(fl):
    fl.close()
    os.remove(fl.name)

# Hilariously overengineered solution to prevent assigning the same identifier
# to more than one site, a temporary file lock is opened in tmp/ while the update
# operation is in progress - preventing the already unlikely scenario that a random
# free Zeal is grabbed between another process grabbing but not finishing the update
def _get_next_free_zeal(db, pool, remaining_attempts=3):
    if remaining_attempts == 0:
        # Prevent looping forever to retry flocks
        return None, None

    # Use func.random to grab random result https://stackoverflow.com/a/60815
    zeal = db.query(models.ZealIdentifier).filter(models.ZealIdentifier.pool == pool, models.ZealIdentifier.is_assigned == False).order_by(func.random()).first()
    if not zeal:
        # Likely depleted
        return None, None

    fl = _open_zeal_lock(zeal.zeal)

    if not zeal and fl:
        return _get_next_free_zeal(db, remaining_attempts-1)
    return zeal, fl


def assign_identifier(db: Session, request: schemas.ZealLinkageAssignmentRequest):
    # Check for assignment and reply
    if request.linkage_id:
        z = get_identifier_from_linkage(db, request.linkage_id)
        if z:
            return z

    # Return the next un-used Zeal and open a lock on it
    zeal, fl = _get_next_free_zeal(db)

    if zeal:
        zeal.is_assigned = True
        zeal.linkage_id = request.linkage_id
        zeal.assigned_to = request.org_code
        zeal.prefix = request.prefix
        zeal.assigned_on = datetime.utcnow()

        db.add(zeal)
        db.commit()
        db.refresh(zeal)

    if fl:
        _close_zeal_lock(fl)

    return zeal

from fastapi import FastAPI, Depends
from fastapi import APIRouter


from zana.database import get_sessionmaker


# Magic dependency https://fastapi.tiangolo.com/tutorial/sql-databases/
def get_db(sessionmaker=get_sessionmaker):
    db = sessionmaker()()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy.orm import Session
from zana import crud, models, schemas

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Hello World"}

@router.post("/add/", response_model=schemas.ZealIdentifier)
def add_identifier(zeal: schemas.ZealIdentifierCreate, db: Session = Depends(get_db)):
    return crud.create_identifier(db=db, zeal=zeal)

@router.post("/issue/", response_model=schemas.ZealIdentifier)
def assign_identifier(request: schemas.ZealLinkageAssignmentRequest, db: Session = Depends(get_db)):

    # Check for assignment and reply
    if request.linkage_id:
        zeal = crud.get_identifier_from_linkage(db, request.linkage_id)
        if zeal:
            return zeal
        else:
            db.rollback()
    return crud.assign_identifier(db=db, request=request)

def get_application():
    app = FastAPI(title="ZANA")
    app.include_router(router)
    return app
app = get_application()

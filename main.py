from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from zana import crud, models, schemas
from zana.database import SessionLocal, engine

app = FastAPI(title="ZANA")

# Magic dependency https://fastapi.tiangolo.com/tutorial/sql-databases/
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/add/", response_model=schemas.ZealIdentifier)
def add_identifier(zeal: schemas.ZealIdentifierCreate, db: Session = Depends(get_db)):
    return crud.create_identifier(db=db, zeal=zeal)

@app.post("/issue/", response_model=schemas.ZealIdentifier)
def assign_identifier(request: schemas.ZealLinkageAssignmentRequest, db: Session = Depends(get_db)):

    # Check for assignment and reply
    if request.linkage_id:
        zeal = crud.get_identifier_from_linkage(db, request.linkage_id)
        if zeal:
            return zeal
        else:
            db.rollback()
    return crud.assign_identifier(db=db, request=request)

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from zana import crud, models, schemas
from zana.database import SessionLocal, engine

app = FastAPI()

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

@app.post("/zeal/", response_model=schemas.ZealIdentifier)
def create_identifier(zeal: schemas.ZealIdentifierCreate, db: Session = Depends(get_db)):
    return crud.create_identifier(db=db, zeal=zeal)

@app.get("/zeal/{zeal}", response_model=schemas.ZealIdentifier)
def detail_identifier(zeal: str, db: Session = Depends(get_db)):
    return crud.get_identifier(db=db, zeal=zeal)

@app.get("/zeal/", response_model=List[schemas.ZealIdentifier])
def list_identifiers(db: Session = Depends(get_db), org_code: str = None, prefix: str = None):
    return crud.list_identifiers(db=db, org_code=org_code, prefix=prefix)

@app.post("/issue/", response_model=List[schemas.ZealIdentifier])
def assign_identifiers(request: schemas.ZealAssignmentRequest, db: Session = Depends(get_db)):
    return crud.assign_identifiers(db=db, request=request)

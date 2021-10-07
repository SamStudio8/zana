from fastapi import FastAPI, Depends, APIRouter, Response
from fastapi.responses import JSONResponse

from zana.database import ZanaEngineSession

# Magic dependency https://fastapi.tiangolo.com/tutorial/sql-databases/
def get_db(sessionmaker=ZanaEngineSession.get_sessionmaker):
    db = sessionmaker()
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

@router.post("/add/", response_model=schemas.ZealIdentifier, status_code=201)
def add_identifier(request: schemas.ZealIdentifierCreate, db: Session = Depends(get_db)):
    zeal = crud.create_identifier(db=db, zeal=request)
    if not zeal:
        return JSONResponse(status_code=409, content={"message": "duplicate zeal", "zeal": request.zeal})
    return zeal

@router.post("/issue/", response_model=schemas.ZealIdentifier)
def issue_identifier(request: schemas.ZealLinkageAssignmentRequest, response: Response, db: Session = Depends(get_db)):

    # Check for assignment and reply
    if request.linkage_id:
        zeal = crud.get_identifier_from_linkage(db, request.linkage_id)
        if zeal:
            response.status_code = 200
            return zeal
    response.status_code = 201
    zeal = crud.assign_identifier(db=db, request=request)

    if not zeal:
        return JSONResponse(status_code=507, content={"message": "out of zeal"})
    return zeal

def get_application():
    app = FastAPI(title="ZANA")
    app.include_router(router)
    return app
app = get_application()

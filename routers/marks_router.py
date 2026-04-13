from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models.marks import Marks
from schemas.marks_schema import MarksCreate, MarksResponse
from auth.dependencies import require_admin
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 CREATE MARKS (ADMIN ONLY)
@router.post(
    "/marks",
    response_model=MarksResponse,
    dependencies=[Depends(require_admin)]
)
def create_marks(mark: MarksCreate, db: Session = Depends(get_db)):

    # Validation
    if mark.internal < 0 or mark.external < 0:
        raise HTTPException(status_code=400, detail="Marks cannot be negative")

    if mark.internal > 40 or mark.external > 60:
        raise HTTPException(status_code=400, detail="Internal max 40 and External max 60 allowed")

    # Duplicate check
    existing = db.query(Marks).filter(
        Marks.student_id == mark.student_id,
        Marks.subject_id == mark.subject_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Marks already exist for this student and subject"
        )

    total_marks = mark.internal + mark.external

    db_mark = Marks(
        student_id=mark.student_id,
        subject_id=mark.subject_id,
        internal=mark.internal,
        external=mark.external,
        total=total_marks
    )

    db.add(db_mark)

    try:
        db.commit()
        db.refresh(db_mark)
        logger.info(f"Marks created: {db_mark.mark_id}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid student_id or subject_id")

    return db_mark


# 📖 READ MARKS (OPEN + PAGINATION)
@router.get("/marks", response_model=list[MarksResponse])
def get_marks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if limit > 100:
        limit = 100

    return db.query(Marks).offset(skip).limit(limit).all()


# 🔐 UPDATE MARKS (ADMIN ONLY)
@router.put(
    "/marks/{mark_id}",
    response_model=MarksResponse,
    dependencies=[Depends(require_admin)]
)
def update_marks(mark_id: int, updated_mark: MarksCreate, db: Session = Depends(get_db)):

    db_mark = db.query(Marks).filter(Marks.mark_id == mark_id).first()

    if not db_mark:
        raise HTTPException(status_code=404, detail="Marks not found")

    if updated_mark.internal < 0 or updated_mark.external < 0:
        raise HTTPException(status_code=400, detail="Marks cannot be negative")

    if updated_mark.internal > 40 or updated_mark.external > 60:
        raise HTTPException(status_code=400, detail="Internal max 40 and External max 60 allowed")

    db_mark.internal = updated_mark.internal
    db_mark.external = updated_mark.external
    db_mark.total = updated_mark.internal + updated_mark.external

    db.commit()
    db.refresh(db_mark)

    logger.info(f"Marks updated: {mark_id}")

    return db_mark


# 🔐 DELETE MARKS (ADMIN ONLY)
@router.delete(
    "/marks/{mark_id}",
    dependencies=[Depends(require_admin)]
)
def delete_marks(mark_id: int, db: Session = Depends(get_db)):

    db_mark = db.query(Marks).filter(Marks.mark_id == mark_id).first()

    if not db_mark:
        raise HTTPException(status_code=404, detail="Marks not found")

    db.delete(db_mark)
    db.commit()

    logger.info(f"Marks deleted: {mark_id}")

    return {
        "status": "success",
        "message": "Marks deleted successfully"
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models.student import Student
from schemas.student_schema import StudentCreate, StudentResponse
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


# 🔐 CREATE STUDENT (ADMIN ONLY)
@router.post(
    "/students",
    response_model=StudentResponse,
    dependencies=[Depends(require_admin)]
)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):

    db_student = Student(**student.dict())
    db.add(db_student)

    try:
        db.commit()
        db.refresh(db_student)
        logger.info(f"Student created: {db_student.student_id}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    return db_student


# 📖 READ STUDENTS (OPEN)
@router.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# 🔐 DELETE STUDENT (ADMIN ONLY)
@router.delete(
    "/students/{student_id}",
    dependencies=[Depends(require_admin)]
)
def delete_student(student_id: int, db: Session = Depends(get_db)):

    db_student = db.query(Student).filter(Student.student_id == student_id).first()

    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(db_student)
    db.commit()

    logger.info(f"Student deleted: {student_id}")

    return {
        "status": "success",
        "message": "Student deleted successfully"
    }
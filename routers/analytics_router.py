from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from auth.dependencies import require_viewer

from services.analytics_service import (
    get_dashboard_data,
    get_class_dashboard,
    calculate_student_average,
    detect_risk_level,
    get_student_rankings,
    get_weak_subject,
    get_topper,
    get_student_summary
)

router = APIRouter(tags=["Analytics"])


# 🔌 DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 📊 ANALYTICS APIs
# =========================

# 🔹 Average + Risk Level
@router.get("/analytics/average/{student_id}")
def get_average(student_id: int, semester: int | None = None, db: Session = Depends(get_db)):

    avg = calculate_student_average(db, student_id, semester)

    if avg is None:
        return {
            "student_id": student_id,
            "message": "No marks available for given semester"
        }

    risk = detect_risk_level(avg)

    return {
        "student_id": student_id,
        "semester": semester,
        "average": avg,
        "risk_level": risk
    }


# 🔹 Rankings
@router.get("/analytics/rankings")
def rankings(semester: int | None = None, db: Session = Depends(get_db)):

    results = get_student_rankings(db, semester)

    if semester is not None and not results:
        return {
            "semester": semester,
            "message": "No students found for this semester"
        }

    return results


# 🔹 Weak Subject
@router.get("/analytics/weak-subject/{student_id}")
def weak_subject(student_id: int, semester: int | None = None, db: Session = Depends(get_db)):

    result = get_weak_subject(db, student_id, semester)

    if not result:
        return {
            "student_id": student_id,
            "message": "No marks available for given semester"
        }

    return result


# 🔹 Topper
@router.get("/analytics/topper")
def topper(semester: int | None = None, db: Session = Depends(get_db)):

    result = get_topper(db, semester)

    if not result:
        if semester is not None:
            return {
                "semester": semester,
                "message": "No students found for this semester"
            }
        return {"message": "No data available"}

    return result


# 🔹 Full Student Summary
@router.get("/analytics/summary/{student_id}")
def student_summary(student_id: int, semester: int | None = None, db: Session = Depends(get_db)):

    result = get_student_summary(db, student_id, semester)

    if not result:
        return {
            "student_id": student_id,
            "message": "No marks available for given semester"
        }

    return result


# =========================
# 📊 DASHBOARD APIs (FIXED)
# =========================

# ✅ CLASS DASHBOARD (STATIC ROUTE FIRST)
@router.get(
    "/dashboard/class",
    dependencies=[Depends(require_viewer)]
)
def class_dashboard(db: Session = Depends(get_db)):
    return get_class_dashboard(db)


# ✅ STUDENT DASHBOARD (RENAMED - NO CONFLICT)
@router.get(
    "/dashboard/student/{student_id}",
    dependencies=[Depends(require_viewer)]
)
def dashboard(student_id: int, db: Session = Depends(get_db)):

    data = get_dashboard_data(db, student_id)

    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    return data
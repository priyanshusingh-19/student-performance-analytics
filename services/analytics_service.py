from sqlalchemy.orm import Session
from sqlalchemy import func
from models.marks import Marks
from models.student import Student
from models.subject import Subject


# -----------------------------
# Calculate Student Average
# -----------------------------
def calculate_student_average(db: Session, student_id: int, semester: int | None = None):

    query = (
        db.query(func.avg(Marks.total))
        .join(Student, Student.student_id == Marks.student_id)
        .filter(Marks.student_id == student_id)
    )

    if semester is not None:
        query = query.filter(Student.semester == semester)

    result = query.scalar()

    if result is None:
        return None

    return round(float(result), 2)


# -----------------------------
# Risk Detection
# -----------------------------
def detect_risk_level(avg: float):
    if avg < 40:
        return "Critical"
    elif avg < 50:
        return "High Risk"
    elif avg < 60:
        return "Moderate Risk"
    elif avg < 75:
        return "Stable"
    else:
        return "Excellent"


# -----------------------------
# Weak Subject
# -----------------------------
def get_weak_subject(db: Session, student_id: int, semester: int | None = None):

    avg_expr = func.avg(Marks.total)

    query = (
        db.query(
            Subject.subject_id,
            Subject.subject_name,
            avg_expr.label("average")
        )
        .join(Marks, Subject.subject_id == Marks.subject_id)
        .join(Student, Student.student_id == Marks.student_id)
        .filter(Marks.student_id == student_id)
        .group_by(Subject.subject_id, Subject.subject_name)
    )

    if semester is not None:
        query = query.filter(Student.semester == semester)

    result = query.order_by(avg_expr.asc()).first()

    if not result:
        return None

    return {
        "student_id": student_id,
        "semester": semester,
        "subject_id": result.subject_id,
        "subject_name": result.subject_name,
        "average": round(float(result.average), 2)
    }


# -----------------------------
# Student Rankings
# -----------------------------
def get_student_rankings(db: Session, semester: int | None = None):

    avg_expr = func.avg(Marks.total)

    query = (
        db.query(
            Student.student_id,
            Student.name,
            Student.semester,
            avg_expr.label("average")
        )
        .join(Marks, Student.student_id == Marks.student_id)
        .group_by(Student.student_id, Student.name, Student.semester)
    )

    # 🔥 Apply semester filter if provided
    if semester is not None:
        query = query.filter(Student.semester == semester)

    results = query.order_by(avg_expr.desc()).all()

    rankings = []
    rank = 1

    for row in results:
        rankings.append({
            "rank": rank,
            "student_id": row.student_id,
            "name": row.name,
            "semester": row.semester,
            "average": round(float(row.average), 2)
        })
        rank += 1

    return rankings


# -----------------------------
# Topper
# -----------------------------
def get_topper(db: Session, semester: int | None = None):

    avg_expr = func.avg(Marks.total)

    query = (
        db.query(
            Student.student_id,
            Student.name,
            Student.semester,
            avg_expr.label("average")
        )
        .join(Marks, Student.student_id == Marks.student_id)
        .group_by(Student.student_id, Student.name, Student.semester)
    )

    if semester is not None:
        query = query.filter(Student.semester == semester)

    result = query.order_by(avg_expr.desc()).first()

    if not result:
        return None

    return {
        "student_id": result.student_id,
        "name": result.name,
        "semester": result.semester,
        "average": round(float(result.average), 2)
    }


# -----------------------------
# Student Summary (Master Endpoint)
# -----------------------------
def get_student_summary(db: Session, student_id: int, semester: int | None = None):

    avg = calculate_student_average(db, student_id, semester)

    if avg is None:
        return None

    weak = get_weak_subject(db, student_id)
    risk = detect_risk_level(avg)

    return {
        "student_id": student_id,
        "semester": semester,
        "average": avg,
        "risk_level": risk,
        "weak_subject": weak["subject_name"] if weak else None
    }


def get_dashboard_data(db: Session, student_id: int):

    # 🔹 Student exists or not
    student = db.query(Student).filter(Student.student_id == student_id).first()

    if not student:
        return None

    # 🔹 Average
    avg = calculate_student_average(db, student_id)

    # 🔹 Risk
    risk = detect_risk_level(avg) if avg > 0 else "No data"

    # 🔹 Weak subject
    weak = get_weak_subject(db, student_id)

    # 🔹 Ranking
    rankings = get_student_rankings(db)

    rank = None
    for r in rankings:
        if r["student_id"] == student_id:
            rank = r["rank"]
            break

    return {
        "student_id": student_id,
        "name": student.name,
        "average": avg,
        "risk_level": risk,
        "weak_subject": weak["subject_name"] if weak else None,
        "rank": rank
    }

def get_class_dashboard(db: Session):

    # 🔹 Total students
    total_students = db.query(Student).count()

    # 🔹 Class average
    avg_result = db.query(func.avg(Marks.total)).scalar()
    class_average = round(float(avg_result), 2) if avg_result else 0

    # 🔹 Topper
    topper = get_topper(db)

    # 🔹 Risk distribution
    students = db.query(Student.student_id).all()

    risk_distribution = {
        "Critical": 0,
        "High Risk": 0,
        "Moderate Risk": 0,
        "Stable": 0,
        "Excellent": 0
    }

    for s in students:
        avg = calculate_student_average(db, s.student_id)

        if avg == 0:
            continue

        risk = detect_risk_level(avg)
        risk_distribution[risk] += 1

    return {
        "total_students": total_students,
        "class_average": class_average,
        "topper": topper,
        "risk_distribution": risk_distribution
    }
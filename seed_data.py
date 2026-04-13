from database import SessionLocal
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.user import User
from auth.auth_utils import hash_password

import random

db = SessionLocal()

# -------------------------------
# 🔥 CLEAN OLD DATA (IMPORTANT)
# -------------------------------
db.query(Marks).delete()
db.query(Student).delete()
db.query(Subject).delete()
db.query(User).delete()
db.commit()


# -------------------------------
# 👤 USERS (AUTH)
# -------------------------------
admin = User(
    username="admin",
    hashed_password=hash_password("admin123"),
    role="admin"
)

viewer = User(
    username="viewer",
    hashed_password=hash_password("viewer123"),
    role="viewer"
)

db.add_all([admin, viewer])
db.commit()


# -------------------------------
# 🎓 SUBJECTS
# -------------------------------
subjects = [
    Subject(subject_name="Maths", credits=4, semester=6),
    Subject(subject_name="DBMS", credits=3, semester=6),
    Subject(subject_name="OS", credits=3, semester=6),
]

db.add_all(subjects)
db.commit()


# -------------------------------
# 👨‍🎓 STUDENTS (10 DATA)
# -------------------------------
students = [
    Student(name="Priyanshu", branch="CSE", semester=6, email="s1@test.com"),
    Student(name="Rahul", branch="IT", semester=5, email="s2@test.com"),
    Student(name="Aman", branch="CSE", semester=6, email="s3@test.com"),
    Student(name="Neha", branch="ECE", semester=4, email="s4@test.com"),
    Student(name="Simran", branch="CSE", semester=6, email="s5@test.com"),
    Student(name="Karan", branch="IT", semester=5, email="s6@test.com"),
    Student(name="Anjali", branch="ECE", semester=4, email="s7@test.com"),
    Student(name="Rohit", branch="CSE", semester=6, email="s8@test.com"),
    Student(name="Pooja", branch="IT", semester=5, email="s9@test.com"),
    Student(name="Vikas", branch="ECE", semester=4, email="s10@test.com"),
]

db.add_all(students)
db.commit()


# -------------------------------
# 📊 MARKS (SMART + REALISTIC)
# -------------------------------
students = db.query(Student).all()
subjects = db.query(Subject).all()

marks_list = []

for student in students:
    for subject in subjects:

        # 🎯 Student type logic
        student_type = student.student_id % 4

        if student_type == 0:  # Topper
            internal = random.randint(32, 40)
            external_marks = random.randint(52, 60)

        elif student_type == 1:  # Average
            internal = random.randint(25, 35)
            external_marks = random.randint(45, 55)

        elif student_type == 2:  # Weak
            internal = random.randint(20, 28)
            external_marks = random.randint(40, 48)

        else:  # Risk / failing
            internal = random.randint(10, 25)
            external_marks = random.randint(30, 45)

        # 🔥 Random failure injection
        if random.random() < 0.15:
            internal = random.randint(5, 15)
            external_marks = random.randint(20, 35)

        total = internal + external_marks

        mark = Marks(
            student_id=student.student_id,
            subject_id=subject.subject_id,
            internal=internal,
            external_marks=external_marks,
            total=total
        )

        marks_list.append(mark)

db.add_all(marks_list)
db.commit()


print("🔥 Database seeded successfully with realistic data!")
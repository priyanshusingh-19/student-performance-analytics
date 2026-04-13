from sqlalchemy import Column, Integer, String
from database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
from sqlalchemy import Column, Integer, String
from database import Base

class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
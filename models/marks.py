from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index
from database import Base

class Marks(Base):
    __tablename__ = "marks"

    mark_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False, index=True)
    internal = Column(Integer, nullable=False)
    external = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="unique_student_subject"),
        Index("idx_student_subject", "student_id", "subject_id"),
    )
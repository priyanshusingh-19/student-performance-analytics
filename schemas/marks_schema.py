from pydantic import BaseModel

class MarksCreate(BaseModel):
    student_id: int
    subject_id: int
    internal: int
    external: int

class MarksResponse(BaseModel):
    mark_id: int
    student_id: int
    subject_id: int
    internal: int
    external: int
    total: int

    class Config:
        from_attributes = True
from pydantic import BaseModel

class SubjectCreate(BaseModel):
    subject_name: str
    credits: int
    semester: int

class SubjectResponse(SubjectCreate):
    subject_id: int

    class Config:
        from_attributes = True
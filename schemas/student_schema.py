from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    name: str
    branch: str
    semester: int
    email: EmailStr

class StudentResponse(StudentCreate):
    student_id: int

    class Config:
        from_attributes = True
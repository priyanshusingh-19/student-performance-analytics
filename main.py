from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from routers import student_router
from routers import subject_router
from routers import marks_router
from routers import analytics_router
from routers import auth_router

# 🚀 CREATE APP FIRST (IMPORTANT)
app = FastAPI(
    title="Student Performance Analytics API",
    version="1.0.0"
)

# 🌐 CORS (AFTER app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🗄️ Create DB tables
Base.metadata.create_all(bind=engine)

# 🔗 Include routers
app.include_router(student_router.router)
app.include_router(subject_router.router)
app.include_router(marks_router.router)
app.include_router(analytics_router.router)
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
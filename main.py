from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from routers import student_router
from routers import subject_router
from routers import marks_router
from routers import analytics_router
from routers import auth_router

from contextlib import asynccontextmanager
from seed_data import seed
import os


# ✅ Lifespan (modern startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App starting...")

    # 🗄️ Create DB tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ensured")

    # 🎯 Controlled seeding
    if os.getenv("SEED_DB") == "true":
        print("🌱 Seeding enabled...")
        seed()
    else:
        print("⏭️ Seeding skipped")

    yield

    print("🛑 App shutting down...")


# ✅ CREATE APP ONLY ONCE
app = FastAPI(
    title="Student Performance Analytics API",
    version="1.0.0",
    lifespan=lifespan
)


# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔗 Routers
app.include_router(student_router.router)
app.include_router(subject_router.router)
app.include_router(marks_router.router)
app.include_router(analytics_router.router)
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])


# 🏠 Root route
@app.get("/")
def home():
    return {
        "message": "Student Performance Analytics API is running 🚀"
    }
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 Engine with connection stability
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # prevents connection drop issues
    pool_recycle=3600     # refresh connection every 1 hour
)

# 🔥 Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔥 Base class for models
Base = declarative_base()
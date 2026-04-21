from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncio

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    preferred_language = Column(String, default="English")

class AppointmentRecord(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    doctor_specialty = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String) # booked, cancelled, rescheduled
    
# Swapped PostgreSQL to SQLite so it runs out-of-the-box without Docker!
DATABASE_URL = "sqlite:///./voice_ai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine, Column, String, Text, Float, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/projectpilot")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProjectAnalysisDB(Base):
    __tablename__ = "project_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_description = Column(Text, nullable=False)

    # Full agent outputs (new comprehensive format)
    intake_analysis = Column(JSON)
    technical_analysis = Column(JSON)
    estimation_analysis = Column(JSON)
    summary_analysis = Column(JSON)

    # Legacy flat fields (for backward compatibility)
    executive_summary = Column(Text)
    tech_stack = Column(JSON)
    architecture_overview = Column(Text)
    team_composition = Column(JSON)
    timeline_breakdown = Column(JSON)
    cost_estimate = Column(JSON)
    risks_and_dependencies = Column(JSON)
    similar_projects = Column(JSON)

    # Metadata
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    user_id = Column(String(255))

class ProjectTemplate(Base):
    __tablename__ = "project_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tech_stack = Column(JSON)
    estimated_duration = Column(Integer)
    estimated_cost = Column(Float)
    team_size = Column(Integer)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    # Import all models to ensure they're registered
    # Database initialization disabled - using CSV files instead
    try:
        from .employee_models import Employee, Skill, EmployeeSkill, HistoricalProject, ProjectAssignment
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"WARNING: Database initialization skipped (using CSV files): {e}")
        pass  # Silently skip database initialization

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
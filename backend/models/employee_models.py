from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(100))
    title = Column(String(200))
    seniority_level = Column(String(50))  # Junior, Mid, Senior, Lead, Principal
    cost_code = Column(String(50))
    hourly_rate = Column(Float, nullable=False)
    annual_salary = Column(Float)
    location = Column(String(100))
    timezone = Column(String(50))
    availability_percentage = Column(Float, default=100.0)  # % available for projects
    is_active = Column(Boolean, default=True)
    hire_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    project_assignments = relationship("ProjectAssignment", back_populates="employee")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # Frontend, Backend, Mobile, AI/ML, DevOps, Design, etc.
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(Integer, nullable=False)  # 1-5 scale
    years_experience = Column(Float)
    is_primary_skill = Column(Boolean, default=False)
    last_used = Column(DateTime)
    certified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

class HistoricalProject(Base):
    __tablename__ = "historical_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    project_code = Column(String(50), unique=True)
    description = Column(Text)
    client_name = Column(String(255))
    industry = Column(String(100))
    project_type = Column(String(100))  # web_app, mobile_app, api, etc.

    # Project metrics
    complexity_score = Column(Integer)  # 1-10 scale
    actual_duration_weeks = Column(Integer)
    estimated_duration_weeks = Column(Integer)
    actual_cost = Column(Float)
    estimated_cost = Column(Float)
    team_size = Column(Integer)

    # Technology used
    tech_stack = Column(JSON)
    architecture_pattern = Column(String(100))

    # Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    delivery_date = Column(DateTime)

    # Success metrics
    on_time_delivery = Column(Boolean, default=True)
    within_budget = Column(Boolean, default=True)
    client_satisfaction = Column(Float)  # 1-5 scale
    quality_score = Column(Float)  # 1-5 scale

    # Lessons learned
    challenges_faced = Column(JSON)
    lessons_learned = Column(Text)
    recommendations = Column(Text)

    # Status
    status = Column(String(50), default="completed")  # completed, cancelled, on_hold
    is_reference_project = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = relationship("ProjectAssignment", back_populates="project")

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("historical_projects.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    role_in_project = Column(String(100), nullable=False)
    allocation_percentage = Column(Float, default=100.0)  # % of time on this project
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    actual_hours = Column(Float)
    hourly_rate_at_time = Column(Float)

    # Performance metrics
    performance_rating = Column(Float)  # 1-5 scale
    feedback = Column(Text)
    key_contributions = Column(JSON)
    skills_used = Column(JSON)
    skills_developed = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="project_assignments")
    project = relationship("HistoricalProject", back_populates="assignments")
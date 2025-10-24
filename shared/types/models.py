from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TechStackCategory(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    AI_ML = "ai_ml"
    INFRASTRUCTURE = "infrastructure"
    MOBILE = "mobile"
    DEVOPS = "devops"

class ProjectInput(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000)
    company_size: Optional[str] = None
    budget_range: Optional[str] = None
    timeline_preference: Optional[str] = None
    industry: Optional[str] = None

class TechStackItem(BaseModel):
    name: str
    category: TechStackCategory
    reason: str
    alternatives: Optional[List[str]] = []

class TeamMember(BaseModel):
    role: str
    seniority_level: str
    hours_per_week: int
    duration_weeks: int
    hourly_rate: float

class RiskItem(BaseModel):
    description: str
    impact: str  # "Low", "Medium", "High"
    mitigation: str

class ProjectEstimate(BaseModel):
    total_cost: float
    duration_weeks: int
    team_size: int
    confidence_score: float = Field(..., ge=0, le=1)

class ProjectAnalysis(BaseModel):
    id: Optional[str] = None
    input_description: str
    executive_summary: str
    tech_stack: List[TechStackItem]
    architecture_overview: str
    team_composition: List[TeamMember]
    timeline_breakdown: Dict[str, int]
    cost_estimate: ProjectEstimate
    risks_and_dependencies: List[RiskItem]
    similar_projects: Optional[List[str]] = []
    status: ProjectStatus = ProjectStatus.PENDING
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AgentResponse(BaseModel):
    agent_name: str
    analysis: Dict[str, Any]
    confidence: float
    processing_time: float
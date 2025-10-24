from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import json
from datetime import datetime
from io import StringIO

from ..models.database import get_db
from ..models.employee_models import Employee, Skill, EmployeeSkill, HistoricalProject, ProjectAssignment
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/import/employees")
async def import_employees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import employees from CSV/Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be CSV or Excel format")

        # Read file content
        content = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(content)

        # Validate required columns
        required_columns = ['employee_id', 'name', 'email', 'hourly_rate']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Import employees
        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Check if employee already exists
                existing_employee = db.query(Employee).filter(
                    Employee.employee_id == row['employee_id']
                ).first()

                if existing_employee:
                    errors.append(f"Row {index + 1}: Employee {row['employee_id']} already exists")
                    continue

                # Create new employee
                employee_data = {
                    'employee_id': row['employee_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'department': row.get('department', ''),
                    'title': row.get('title', ''),
                    'seniority_level': row.get('seniority_level', 'Mid'),
                    'cost_code': row.get('cost_code', ''),
                    'hourly_rate': float(row['hourly_rate']),
                    'annual_salary': float(row.get('annual_salary', 0)) if pd.notna(row.get('annual_salary')) else None,
                    'location': row.get('location', ''),
                    'timezone': row.get('timezone', ''),
                    'availability_percentage': float(row.get('availability_percentage', 100.0)),
                    'hire_date': pd.to_datetime(row.get('hire_date')).date() if pd.notna(row.get('hire_date')) else None,
                    'is_active': bool(row.get('is_active', True))
                }

                employee = Employee(**employee_data)
                db.add(employee)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        db.commit()

        return {
            "message": f"Successfully imported {imported_count} employees",
            "imported_count": imported_count,
            "total_rows": len(df),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error importing employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/skills")
async def import_skills(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import skills from CSV/Excel file"""
    try:
        # Read and validate file
        content = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(content)

        required_columns = ['name', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Check if skill already exists
                existing_skill = db.query(Skill).filter(
                    Skill.name == row['name']
                ).first()

                if existing_skill:
                    errors.append(f"Row {index + 1}: Skill {row['name']} already exists")
                    continue

                skill = Skill(
                    name=row['name'],
                    category=row['category'],
                    description=row.get('description', '')
                )
                db.add(skill)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        db.commit()

        return {
            "message": f"Successfully imported {imported_count} skills",
            "imported_count": imported_count,
            "total_rows": len(df),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error importing skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/employee-skills")
async def import_employee_skills(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import employee skills from CSV/Excel file"""
    try:
        content = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(content)

        required_columns = ['employee_id', 'skill_name', 'proficiency_level']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Find employee and skill
                employee = db.query(Employee).filter(
                    Employee.employee_id == row['employee_id']
                ).first()

                if not employee:
                    errors.append(f"Row {index + 1}: Employee {row['employee_id']} not found")
                    continue

                skill = db.query(Skill).filter(
                    Skill.name == row['skill_name']
                ).first()

                if not skill:
                    errors.append(f"Row {index + 1}: Skill {row['skill_name']} not found")
                    continue

                # Check if employee skill already exists
                existing_skill = db.query(EmployeeSkill).filter(
                    EmployeeSkill.employee_id == employee.id,
                    EmployeeSkill.skill_id == skill.id
                ).first()

                if existing_skill:
                    errors.append(f"Row {index + 1}: Employee {row['employee_id']} already has skill {row['skill_name']}")
                    continue

                employee_skill = EmployeeSkill(
                    employee_id=employee.id,
                    skill_id=skill.id,
                    proficiency_level=int(row['proficiency_level']),
                    years_experience=float(row.get('years_experience', 0)) if pd.notna(row.get('years_experience')) else None,
                    is_primary_skill=bool(row.get('is_primary_skill', False)),
                    certified=bool(row.get('certified', False)),
                    last_used=pd.to_datetime(row.get('last_used')).date() if pd.notna(row.get('last_used')) else None
                )
                db.add(employee_skill)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        db.commit()

        return {
            "message": f"Successfully imported {imported_count} employee skills",
            "imported_count": imported_count,
            "total_rows": len(df),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error importing employee skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/projects")
async def import_projects(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import historical projects from CSV/Excel file"""
    try:
        content = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(content)

        required_columns = ['project_name', 'project_code', 'project_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Check if project already exists
                existing_project = db.query(HistoricalProject).filter(
                    HistoricalProject.project_code == row['project_code']
                ).first()

                if existing_project:
                    errors.append(f"Row {index + 1}: Project {row['project_code']} already exists")
                    continue

                # Build tech stack JSON
                tech_stack = {}
                if pd.notna(row.get('tech_stack_frontend')):
                    tech_stack['frontend'] = row['tech_stack_frontend']
                if pd.notna(row.get('tech_stack_backend')):
                    tech_stack['backend'] = row['tech_stack_backend']
                if pd.notna(row.get('tech_stack_database')):
                    tech_stack['database'] = row['tech_stack_database']

                project = HistoricalProject(
                    project_name=row['project_name'],
                    project_code=row['project_code'],
                    description=row.get('description', ''),
                    client_name=row.get('client_name', ''),
                    industry=row.get('industry', ''),
                    project_type=row['project_type'],
                    complexity_score=int(row.get('complexity_score', 5)) if pd.notna(row.get('complexity_score')) else None,
                    actual_duration_weeks=int(row.get('actual_duration_weeks', 0)) if pd.notna(row.get('actual_duration_weeks')) else None,
                    estimated_duration_weeks=int(row.get('estimated_duration_weeks', 0)) if pd.notna(row.get('estimated_duration_weeks')) else None,
                    actual_cost=float(row.get('actual_cost', 0)) if pd.notna(row.get('actual_cost')) else None,
                    estimated_cost=float(row.get('estimated_cost', 0)) if pd.notna(row.get('estimated_cost')) else None,
                    team_size=int(row.get('team_size', 0)) if pd.notna(row.get('team_size')) else None,
                    tech_stack=tech_stack if tech_stack else None,
                    architecture_pattern=row.get('architecture_pattern', ''),
                    start_date=pd.to_datetime(row.get('start_date')).date() if pd.notna(row.get('start_date')) else None,
                    end_date=pd.to_datetime(row.get('end_date')).date() if pd.notna(row.get('end_date')) else None,
                    delivery_date=pd.to_datetime(row.get('delivery_date')).date() if pd.notna(row.get('delivery_date')) else None,
                    on_time_delivery=bool(row.get('on_time_delivery', True)),
                    within_budget=bool(row.get('within_budget', True)),
                    client_satisfaction=float(row.get('client_satisfaction', 0)) if pd.notna(row.get('client_satisfaction')) else None,
                    quality_score=float(row.get('quality_score', 0)) if pd.notna(row.get('quality_score')) else None,
                    status=row.get('status', 'completed'),
                    lessons_learned=row.get('lessons_learned', '')
                )
                db.add(project)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        db.commit()

        return {
            "message": f"Successfully imported {imported_count} projects",
            "imported_count": imported_count,
            "total_rows": len(df),
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Error importing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/template/{data_type}")
async def download_template(data_type: str):
    """Download data import template"""
    try:
        from fastapi.responses import FileResponse
        import os

        templates_dir = "data/templates"

        template_files = {
            "employees": f"{templates_dir}/employees_template.csv",
            "skills": f"{templates_dir}/skills_template.csv",
            "employee_skills": f"{templates_dir}/employee_skills_template.csv",
            "projects": f"{templates_dir}/projects_template.csv",
            "project_assignments": f"{templates_dir}/project_assignments_template.csv"
        }

        if data_type not in template_files:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid template type. Available: {', '.join(template_files.keys())}"
            )

        file_path = template_files[data_type]

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Template file not found")

        return FileResponse(
            file_path,
            media_type="text/csv",
            filename=f"{data_type}_template.csv"
        )

    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/sample/{data_type}")
async def download_sample_data(data_type: str):
    """Download sample data files"""
    try:
        from fastapi.responses import FileResponse
        import os

        samples_dir = "data/samples"

        sample_files = {
            "employees": f"{samples_dir}/sample_employees.csv",
            "employee_skills": f"{samples_dir}/sample_employee_skills.csv",
            "projects": f"{samples_dir}/sample_projects.csv",
            "project_assignments": f"{samples_dir}/sample_project_assignments.csv"
        }

        if data_type not in sample_files:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sample type. Available: {', '.join(sample_files.keys())}"
            )

        file_path = sample_files[data_type]

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Sample file not found")

        return FileResponse(
            file_path,
            media_type="text/csv",
            filename=f"sample_{data_type}.csv"
        )

    except Exception as e:
        logger.error(f"Error downloading sample data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed-sample-data")
async def seed_sample_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Seed database with sample data"""
    try:
        background_tasks.add_task(run_sample_data_seed)

        return {
            "message": "Sample data seeding started in background",
            "status": "processing"
        }

    except Exception as e:
        logger.error(f"Error starting sample data seed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_sample_data_seed():
    """Background task to seed sample data"""
    try:
        from ..utils.sample_data import populate_sample_data
        populate_sample_data()
        logger.info("Sample data seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding sample data: {str(e)}")
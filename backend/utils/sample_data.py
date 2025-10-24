from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from ..models.employee_models import Employee, Skill, EmployeeSkill, HistoricalProject, ProjectAssignment
from ..models.database import SessionLocal

def create_sample_skills():
    """Create sample skills data"""
    skills_data = [
        # Frontend
        {"name": "React", "category": "Frontend", "description": "JavaScript library for building user interfaces"},
        {"name": "Vue.js", "category": "Frontend", "description": "Progressive JavaScript framework"},
        {"name": "Angular", "category": "Frontend", "description": "TypeScript-based web application framework"},
        {"name": "Next.js", "category": "Frontend", "description": "React framework for production"},
        {"name": "TypeScript", "category": "Frontend", "description": "Typed superset of JavaScript"},
        {"name": "HTML/CSS", "category": "Frontend", "description": "Markup and styling languages"},
        {"name": "Tailwind CSS", "category": "Frontend", "description": "Utility-first CSS framework"},

        # Backend
        {"name": "Python", "category": "Backend", "description": "High-level programming language"},
        {"name": "FastAPI", "category": "Backend", "description": "Modern Python web framework"},
        {"name": "Django", "category": "Backend", "description": "Python web framework"},
        {"name": "Node.js", "category": "Backend", "description": "JavaScript runtime for server-side development"},
        {"name": "Express.js", "category": "Backend", "description": "Node.js web application framework"},
        {"name": "Java", "category": "Backend", "description": "Object-oriented programming language"},
        {"name": "Spring Boot", "category": "Backend", "description": "Java framework for microservices"},
        {"name": "C#", "category": "Backend", "description": "Microsoft programming language"},
        {"name": ".NET", "category": "Backend", "description": "Microsoft development platform"},

        # Mobile
        {"name": "React Native", "category": "Mobile", "description": "Cross-platform mobile development"},
        {"name": "Flutter", "category": "Mobile", "description": "Google's UI toolkit for mobile"},
        {"name": "Swift", "category": "Mobile", "description": "Apple's programming language for iOS"},
        {"name": "Kotlin", "category": "Mobile", "description": "Modern programming language for Android"},

        # Database
        {"name": "PostgreSQL", "category": "Database", "description": "Advanced open-source relational database"},
        {"name": "MySQL", "category": "Database", "description": "Popular relational database"},
        {"name": "MongoDB", "category": "Database", "description": "NoSQL document database"},
        {"name": "Redis", "category": "Database", "description": "In-memory data structure store"},

        # AI/ML
        {"name": "TensorFlow", "category": "AI/ML", "description": "Machine learning framework"},
        {"name": "PyTorch", "category": "AI/ML", "description": "Deep learning framework"},
        {"name": "OpenAI API", "category": "AI/ML", "description": "AI language model API"},
        {"name": "Scikit-learn", "category": "AI/ML", "description": "Machine learning library for Python"},

        # DevOps
        {"name": "Docker", "category": "DevOps", "description": "Containerization platform"},
        {"name": "Kubernetes", "category": "DevOps", "description": "Container orchestration platform"},
        {"name": "AWS", "category": "DevOps", "description": "Amazon Web Services cloud platform"},
        {"name": "Azure", "category": "DevOps", "description": "Microsoft cloud platform"},
        {"name": "GitHub Actions", "category": "DevOps", "description": "CI/CD automation platform"},

        # Design
        {"name": "UI/UX Design", "category": "Design", "description": "User interface and experience design"},
        {"name": "Figma", "category": "Design", "description": "Collaborative design tool"},
        {"name": "Adobe Creative Suite", "category": "Design", "description": "Design and multimedia software"}
    ]

    db = SessionLocal()
    try:
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.add(skill)
        db.commit()
        print(f"Created {len(skills_data)} skills")
    finally:
        db.close()

def create_sample_employees():
    """Create sample employee data"""
    employees_data = [
        {
            "employee_id": "EMP001",
            "name": "Sarah Chen",
            "email": "sarah.chen@company.com",
            "department": "Engineering",
            "title": "Senior Frontend Developer",
            "seniority_level": "Senior",
            "cost_code": "ENG-FE-001",
            "hourly_rate": 95.0,
            "annual_salary": 120000,
            "location": "San Francisco, CA",
            "timezone": "PST",
            "availability_percentage": 90.0,
            "hire_date": datetime(2020, 3, 15),
            "skills": [
                {"skill_name": "React", "proficiency": 5, "years_experience": 4.0, "is_primary": True},
                {"skill_name": "TypeScript", "proficiency": 4, "years_experience": 3.0},
                {"skill_name": "Next.js", "proficiency": 4, "years_experience": 2.0},
                {"skill_name": "Tailwind CSS", "proficiency": 4, "years_experience": 2.5}
            ]
        },
        {
            "employee_id": "EMP002",
            "name": "Marcus Johnson",
            "email": "marcus.johnson@company.com",
            "department": "Engineering",
            "title": "Lead Backend Developer",
            "seniority_level": "Lead",
            "cost_code": "ENG-BE-001",
            "hourly_rate": 115.0,
            "annual_salary": 150000,
            "location": "Austin, TX",
            "timezone": "CST",
            "availability_percentage": 85.0,
            "hire_date": datetime(2018, 7, 22),
            "skills": [
                {"skill_name": "Python", "proficiency": 5, "years_experience": 6.0, "is_primary": True},
                {"skill_name": "FastAPI", "proficiency": 5, "years_experience": 3.0},
                {"skill_name": "PostgreSQL", "proficiency": 4, "years_experience": 5.0},
                {"skill_name": "Docker", "proficiency": 4, "years_experience": 4.0},
                {"skill_name": "AWS", "proficiency": 3, "years_experience": 3.0}
            ]
        },
        {
            "employee_id": "EMP003",
            "name": "Elena Rodriguez",
            "email": "elena.rodriguez@company.com",
            "department": "Engineering",
            "title": "Mobile Developer",
            "seniority_level": "Mid",
            "cost_code": "ENG-MOB-001",
            "hourly_rate": 75.0,
            "annual_salary": 95000,
            "location": "Miami, FL",
            "timezone": "EST",
            "availability_percentage": 100.0,
            "hire_date": datetime(2021, 1, 10),
            "skills": [
                {"skill_name": "React Native", "proficiency": 4, "years_experience": 3.0, "is_primary": True},
                {"skill_name": "Swift", "proficiency": 3, "years_experience": 2.0},
                {"skill_name": "Kotlin", "proficiency": 3, "years_experience": 2.0},
                {"skill_name": "React", "proficiency": 4, "years_experience": 3.5}
            ]
        },
        {
            "employee_id": "EMP004",
            "name": "David Kim",
            "email": "david.kim@company.com",
            "department": "AI/ML",
            "title": "AI Engineer",
            "seniority_level": "Senior",
            "cost_code": "AI-ENG-001",
            "hourly_rate": 125.0,
            "annual_salary": 140000,
            "location": "Seattle, WA",
            "timezone": "PST",
            "availability_percentage": 80.0,
            "hire_date": datetime(2019, 9, 5),
            "skills": [
                {"skill_name": "Python", "proficiency": 5, "years_experience": 5.0, "is_primary": True},
                {"skill_name": "TensorFlow", "proficiency": 4, "years_experience": 3.0},
                {"skill_name": "PyTorch", "proficiency": 4, "years_experience": 2.5},
                {"skill_name": "OpenAI API", "proficiency": 5, "years_experience": 2.0}
            ]
        },
        {
            "employee_id": "EMP005",
            "name": "Jennifer Walsh",
            "email": "jennifer.walsh@company.com",
            "department": "DevOps",
            "title": "DevOps Engineer",
            "seniority_level": "Mid",
            "cost_code": "DEVOPS-001",
            "hourly_rate": 85.0,
            "annual_salary": 110000,
            "location": "Denver, CO",
            "timezone": "MST",
            "availability_percentage": 95.0,
            "hire_date": datetime(2020, 11, 18),
            "skills": [
                {"skill_name": "Docker", "proficiency": 5, "years_experience": 4.0, "is_primary": True},
                {"skill_name": "Kubernetes", "proficiency": 4, "years_experience": 2.0},
                {"skill_name": "AWS", "proficiency": 4, "years_experience": 3.0},
                {"skill_name": "GitHub Actions", "proficiency": 4, "years_experience": 2.5}
            ]
        },
        {
            "employee_id": "EMP006",
            "name": "Alex Thompson",
            "email": "alex.thompson@company.com",
            "department": "Design",
            "title": "UI/UX Designer",
            "seniority_level": "Senior",
            "cost_code": "DES-UX-001",
            "hourly_rate": 80.0,
            "annual_salary": 105000,
            "location": "Portland, OR",
            "timezone": "PST",
            "availability_percentage": 90.0,
            "hire_date": datetime(2019, 5, 12),
            "skills": [
                {"skill_name": "UI/UX Design", "proficiency": 5, "years_experience": 6.0, "is_primary": True},
                {"skill_name": "Figma", "proficiency": 5, "years_experience": 4.0},
                {"skill_name": "Adobe Creative Suite", "proficiency": 4, "years_experience": 5.0}
            ]
        },
        {
            "employee_id": "EMP007",
            "name": "Robert Brown",
            "email": "robert.brown@company.com",
            "department": "Engineering",
            "title": "Junior Full Stack Developer",
            "seniority_level": "Junior",
            "cost_code": "ENG-FS-001",
            "hourly_rate": 45.0,
            "annual_salary": 70000,
            "location": "Chicago, IL",
            "timezone": "CST",
            "availability_percentage": 100.0,
            "hire_date": datetime(2022, 8, 1),
            "skills": [
                {"skill_name": "React", "proficiency": 3, "years_experience": 1.5},
                {"skill_name": "Node.js", "proficiency": 3, "years_experience": 1.5, "is_primary": True},
                {"skill_name": "MongoDB", "proficiency": 2, "years_experience": 1.0},
                {"skill_name": "Express.js", "proficiency": 3, "years_experience": 1.5}
            ]
        },
        {
            "employee_id": "EMP008",
            "name": "Lisa Anderson",
            "email": "lisa.anderson@company.com",
            "department": "QA",
            "title": "QA Engineer",
            "seniority_level": "Mid",
            "cost_code": "QA-001",
            "hourly_rate": 65.0,
            "annual_salary": 85000,
            "location": "Boston, MA",
            "timezone": "EST",
            "availability_percentage": 100.0,
            "hire_date": datetime(2021, 6, 14),
            "skills": [
                {"skill_name": "Python", "proficiency": 3, "years_experience": 2.0},
                {"skill_name": "TypeScript", "proficiency": 3, "years_experience": 2.0, "is_primary": True}
            ]
        }
    ]

    db = SessionLocal()
    try:
        # Get all skills for lookup
        skills = {skill.name: skill for skill in db.query(Skill).all()}

        for emp_data in employees_data:
            # Extract skills data
            skills_data = emp_data.pop("skills", [])

            # Create employee
            employee = Employee(**emp_data)
            db.add(employee)
            db.flush()  # Get the employee ID

            # Add skills
            for skill_data in skills_data:
                skill_name = skill_data["skill_name"]
                if skill_name in skills:
                    employee_skill = EmployeeSkill(
                        employee_id=employee.id,
                        skill_id=skills[skill_name].id,
                        proficiency_level=skill_data["proficiency"],
                        years_experience=skill_data["years_experience"],
                        is_primary_skill=skill_data.get("is_primary", False)
                    )
                    db.add(employee_skill)

        db.commit()
        print(f"Created {len(employees_data)} employees with skills")
    finally:
        db.close()

def create_sample_projects():
    """Create sample historical project data"""
    projects_data = [
        {
            "project_name": "E-commerce Mobile App",
            "project_code": "PROJ001",
            "description": "Cross-platform mobile app for online retail with payment integration",
            "client_name": "RetailCorp Inc",
            "industry": "E-commerce",
            "project_type": "mobile_app",
            "complexity_score": 7,
            "actual_duration_weeks": 24,
            "estimated_duration_weeks": 20,
            "actual_cost": 180000,
            "estimated_cost": 150000,
            "team_size": 5,
            "tech_stack": {
                "frontend": "React Native",
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "payments": "Stripe",
                "cloud": "AWS"
            },
            "architecture_pattern": "microservices",
            "start_date": datetime(2022, 1, 15),
            "end_date": datetime(2022, 7, 10),
            "delivery_date": datetime(2022, 7, 15),
            "on_time_delivery": False,
            "within_budget": False,
            "client_satisfaction": 4.2,
            "quality_score": 4.5,
            "challenges_faced": [
                "Payment gateway integration complexity",
                "iOS app store approval delays",
                "Performance optimization for low-end devices"
            ],
            "lessons_learned": "Allocate more time for third-party integrations and app store processes",
            "assignments": [
                {"employee_id": "EMP001", "role": "Frontend Lead", "allocation": 80, "hours": 768, "rating": 4.5},
                {"employee_id": "EMP002", "role": "Backend Lead", "allocation": 70, "hours": 672, "rating": 4.8},
                {"employee_id": "EMP003", "role": "Mobile Developer", "allocation": 100, "hours": 960, "rating": 4.3},
                {"employee_id": "EMP005", "role": "DevOps Engineer", "allocation": 40, "hours": 384, "rating": 4.6},
                {"employee_id": "EMP008", "role": "QA Engineer", "allocation": 60, "hours": 576, "rating": 4.4}
            ]
        },
        {
            "project_name": "AI-Powered Analytics Dashboard",
            "project_code": "PROJ002",
            "description": "Business intelligence dashboard with ML-driven insights",
            "client_name": "DataTech Solutions",
            "industry": "Analytics",
            "project_type": "web_app",
            "complexity_score": 8,
            "actual_duration_weeks": 16,
            "estimated_duration_weeks": 18,
            "actual_cost": 120000,
            "estimated_cost": 130000,
            "team_size": 4,
            "tech_stack": {
                "frontend": "React",
                "backend": "Python/FastAPI",
                "database": "PostgreSQL",
                "ml": "TensorFlow",
                "visualization": "D3.js",
                "cloud": "AWS"
            },
            "architecture_pattern": "layered",
            "start_date": datetime(2022, 8, 1),
            "end_date": datetime(2022, 12, 15),
            "delivery_date": datetime(2022, 12, 10),
            "on_time_delivery": True,
            "within_budget": True,
            "client_satisfaction": 4.8,
            "quality_score": 4.7,
            "challenges_faced": [
                "Large dataset processing performance",
                "Complex ML model deployment"
            ],
            "lessons_learned": "Early performance testing and incremental ML model deployment",
            "assignments": [
                {"employee_id": "EMP001", "role": "Frontend Developer", "allocation": 90, "hours": 576, "rating": 4.6},
                {"employee_id": "EMP002", "role": "Backend Developer", "allocation": 80, "hours": 512, "rating": 4.9},
                {"employee_id": "EMP004", "role": "AI Engineer", "allocation": 100, "hours": 640, "rating": 4.8},
                {"employee_id": "EMP008", "role": "QA Engineer", "allocation": 50, "hours": 320, "rating": 4.5}
            ]
        },
        {
            "project_name": "Corporate Website Redesign",
            "project_code": "PROJ003",
            "description": "Modern responsive website with CMS integration",
            "client_name": "Corporate Services Ltd",
            "industry": "Professional Services",
            "project_type": "web_app",
            "complexity_score": 4,
            "actual_duration_weeks": 8,
            "estimated_duration_weeks": 8,
            "actual_cost": 45000,
            "estimated_cost": 40000,
            "team_size": 3,
            "tech_stack": {
                "frontend": "Next.js",
                "cms": "Strapi",
                "database": "PostgreSQL",
                "hosting": "Vercel"
            },
            "architecture_pattern": "jamstack",
            "start_date": datetime(2023, 2, 1),
            "end_date": datetime(2023, 4, 1),
            "delivery_date": datetime(2023, 3, 28),
            "on_time_delivery": True,
            "within_budget": False,
            "client_satisfaction": 4.6,
            "quality_score": 4.4,
            "challenges_faced": [
                "Content migration complexity",
                "SEO optimization requirements"
            ],
            "lessons_learned": "Plan content migration early in the project timeline",
            "assignments": [
                {"employee_id": "EMP001", "role": "Frontend Developer", "allocation": 100, "hours": 320, "rating": 4.7},
                {"employee_id": "EMP006", "role": "UI/UX Designer", "allocation": 80, "hours": 256, "rating": 4.8},
                {"employee_id": "EMP007", "role": "Junior Developer", "allocation": 60, "hours": 192, "rating": 4.2}
            ]
        }
    ]

    db = SessionLocal()
    try:
        employees = {emp.employee_id: emp for emp in db.query(Employee).all()}

        for proj_data in projects_data:
            # Extract assignments data
            assignments_data = proj_data.pop("assignments", [])

            # Create project
            project = HistoricalProject(**proj_data)
            db.add(project)
            db.flush()  # Get the project ID

            # Add assignments
            for assignment_data in assignments_data:
                emp_id = assignment_data["employee_id"]
                if emp_id in employees:
                    assignment = ProjectAssignment(
                        project_id=project.id,
                        employee_id=employees[emp_id].id,
                        role_in_project=assignment_data["role"],
                        allocation_percentage=assignment_data["allocation"],
                        actual_hours=assignment_data["hours"],
                        performance_rating=assignment_data["rating"],
                        start_date=project.start_date,
                        end_date=project.end_date,
                        hourly_rate_at_time=employees[emp_id].hourly_rate
                    )
                    db.add(assignment)

        db.commit()
        print(f"Created {len(projects_data)} historical projects with assignments")
    finally:
        db.close()

def populate_sample_data():
    """Populate database with all sample data"""
    print("Creating sample skills...")
    create_sample_skills()

    print("Creating sample employees...")
    create_sample_employees()

    print("Creating sample projects...")
    create_sample_projects()

    print("Sample data creation completed!")

if __name__ == "__main__":
    populate_sample_data()
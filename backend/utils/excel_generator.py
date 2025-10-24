import pandas as pd
from datetime import datetime, timedelta
import os

def create_excel_templates():
    """Create Excel templates for data import"""

    # Employees template
    employees_template = pd.DataFrame({
        'employee_id': ['EMP001', 'EMP002', 'EMP003'],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'email': ['john.doe@company.com', 'jane.smith@company.com', 'bob.johnson@company.com'],
        'department': ['Engineering', 'Engineering', 'Design'],
        'title': ['Senior Developer', 'Frontend Developer', 'UI/UX Designer'],
        'seniority_level': ['Senior', 'Mid', 'Senior'],
        'cost_code': ['ENG-001', 'ENG-002', 'DES-001'],
        'hourly_rate': [95.0, 75.0, 80.0],
        'annual_salary': [120000, 95000, 105000],
        'location': ['San Francisco, CA', 'Austin, TX', 'Portland, OR'],
        'timezone': ['PST', 'CST', 'PST'],
        'availability_percentage': [90.0, 100.0, 85.0],
        'hire_date': ['2020-03-15', '2021-01-10', '2019-05-12'],
        'is_active': [True, True, True]
    })

    # Skills template
    skills_template = pd.DataFrame({
        'name': ['React', 'Python', 'UI/UX Design', 'FastAPI', 'Figma'],
        'category': ['Frontend', 'Backend', 'Design', 'Backend', 'Design'],
        'description': [
            'JavaScript library for building user interfaces',
            'High-level programming language',
            'User interface and experience design',
            'Modern Python web framework',
            'Collaborative design tool'
        ]
    })

    # Employee Skills template
    employee_skills_template = pd.DataFrame({
        'employee_id': ['EMP001', 'EMP001', 'EMP002', 'EMP002', 'EMP003'],
        'skill_name': ['React', 'TypeScript', 'Python', 'FastAPI', 'UI/UX Design'],
        'proficiency_level': [5, 4, 5, 4, 5],
        'years_experience': [4.0, 3.0, 6.0, 3.0, 6.0],
        'is_primary_skill': [True, False, True, False, True],
        'certified': [False, False, True, False, True],
        'last_used': ['2023-10-01', '2023-10-01', '2023-10-01', '2023-10-01', '2023-10-01']
    })

    # Historical Projects template
    projects_template = pd.DataFrame({
        'project_name': ['E-commerce Platform', 'Analytics Dashboard', 'Corporate Website'],
        'project_code': ['PROJ001', 'PROJ002', 'PROJ003'],
        'description': [
            'Full-featured e-commerce platform with payment integration',
            'Business intelligence dashboard with ML insights',
            'Modern responsive corporate website'
        ],
        'client_name': ['RetailCorp Inc', 'DataTech Solutions', 'Corporate Services Ltd'],
        'industry': ['E-commerce', 'Analytics', 'Professional Services'],
        'project_type': ['web_app', 'web_app', 'website'],
        'complexity_score': [8, 7, 4],
        'actual_duration_weeks': [24, 16, 8],
        'estimated_duration_weeks': [20, 18, 8],
        'actual_cost': [180000, 120000, 45000],
        'estimated_cost': [150000, 130000, 40000],
        'team_size': [5, 4, 3],
        'tech_stack_frontend': ['React', 'React', 'Next.js'],
        'tech_stack_backend': ['FastAPI', 'FastAPI', 'Node.js'],
        'tech_stack_database': ['PostgreSQL', 'PostgreSQL', 'PostgreSQL'],
        'architecture_pattern': ['microservices', 'layered', 'jamstack'],
        'start_date': ['2022-01-15', '2022-08-01', '2023-02-01'],
        'end_date': ['2022-07-10', '2022-12-15', '2023-04-01'],
        'delivery_date': ['2022-07-15', '2022-12-10', '2023-03-28'],
        'on_time_delivery': [False, True, True],
        'within_budget': [False, True, False],
        'client_satisfaction': [4.2, 4.8, 4.6],
        'quality_score': [4.5, 4.7, 4.4],
        'status': ['completed', 'completed', 'completed'],
        'lessons_learned': [
            'Allocate more time for third-party integrations',
            'Early performance testing is crucial',
            'Plan content migration early'
        ]
    })

    # Project Assignments template
    assignments_template = pd.DataFrame({
        'project_code': ['PROJ001', 'PROJ001', 'PROJ001', 'PROJ002', 'PROJ002'],
        'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP001', 'EMP002'],
        'role_in_project': ['Frontend Lead', 'Backend Lead', 'UI Designer', 'Frontend Dev', 'Backend Dev'],
        'allocation_percentage': [80, 70, 60, 90, 80],
        'start_date': ['2022-01-15', '2022-01-15', '2022-02-01', '2022-08-01', '2022-08-01'],
        'end_date': ['2022-07-10', '2022-07-10', '2022-06-01', '2022-12-15', '2022-12-15'],
        'actual_hours': [768, 672, 480, 576, 512],
        'hourly_rate_at_time': [90.0, 110.0, 75.0, 95.0, 115.0],
        'performance_rating': [4.5, 4.8, 4.3, 4.6, 4.9],
        'key_contributions': [
            'Led frontend architecture design',
            'Implemented scalable API design',
            'Created user-centered design system',
            'Built responsive dashboard components',
            'Optimized database performance'
        ]
    })

    # Create templates directory if it doesn't exist
    templates_dir = 'data/templates'
    os.makedirs(templates_dir, exist_ok=True)

    # Save templates to Excel files
    with pd.ExcelWriter(f'{templates_dir}/employees_template.xlsx', engine='openpyxl') as writer:
        employees_template.to_excel(writer, sheet_name='Employees', index=False)
        # Add instructions sheet
        instructions = pd.DataFrame({
            'Field': ['employee_id', 'name', 'email', 'seniority_level', 'hourly_rate', 'availability_percentage'],
            'Description': [
                'Unique identifier for employee (e.g., EMP001)',
                'Full name of the employee',
                'Work email address',
                'Junior/Mid/Senior/Lead/Principal',
                'Hourly billing rate in USD',
                'Percentage available for projects (0-100)'
            ],
            'Required': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No'],
            'Example': ['EMP001', 'John Doe', 'john@company.com', 'Senior', '95.0', '90.0']
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)

    with pd.ExcelWriter(f'{templates_dir}/skills_template.xlsx', engine='openpyxl') as writer:
        skills_template.to_excel(writer, sheet_name='Skills', index=False)
        employee_skills_template.to_excel(writer, sheet_name='Employee_Skills', index=False)

    with pd.ExcelWriter(f'{templates_dir}/projects_template.xlsx', engine='openpyxl') as writer:
        projects_template.to_excel(writer, sheet_name='Projects', index=False)
        assignments_template.to_excel(writer, sheet_name='Assignments', index=False)

    print(f"Excel templates created in {templates_dir}/")

def create_sample_excel_files():
    """Create sample Excel files with realistic data"""

    # Sample employees with more data
    sample_employees = pd.DataFrame({
        'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005', 'EMP006', 'EMP007', 'EMP008'],
        'name': [
            'Sarah Chen', 'Marcus Johnson', 'Elena Rodriguez', 'David Kim',
            'Jennifer Walsh', 'Alex Thompson', 'Robert Brown', 'Lisa Anderson'
        ],
        'email': [
            'sarah.chen@company.com', 'marcus.johnson@company.com', 'elena.rodriguez@company.com',
            'david.kim@company.com', 'jennifer.walsh@company.com', 'alex.thompson@company.com',
            'robert.brown@company.com', 'lisa.anderson@company.com'
        ],
        'department': [
            'Engineering', 'Engineering', 'Engineering', 'AI/ML',
            'DevOps', 'Design', 'Engineering', 'QA'
        ],
        'title': [
            'Senior Frontend Developer', 'Lead Backend Developer', 'Mobile Developer', 'AI Engineer',
            'DevOps Engineer', 'UI/UX Designer', 'Junior Full Stack Developer', 'QA Engineer'
        ],
        'seniority_level': ['Senior', 'Lead', 'Mid', 'Senior', 'Mid', 'Senior', 'Junior', 'Mid'],
        'cost_code': [
            'ENG-FE-001', 'ENG-BE-001', 'ENG-MOB-001', 'AI-ENG-001',
            'DEVOPS-001', 'DES-UX-001', 'ENG-FS-001', 'QA-001'
        ],
        'hourly_rate': [95.0, 115.0, 75.0, 125.0, 85.0, 80.0, 45.0, 65.0],
        'annual_salary': [120000, 150000, 95000, 140000, 110000, 105000, 70000, 85000],
        'location': [
            'San Francisco, CA', 'Austin, TX', 'Miami, FL', 'Seattle, WA',
            'Denver, CO', 'Portland, OR', 'Chicago, IL', 'Boston, MA'
        ],
        'timezone': ['PST', 'CST', 'EST', 'PST', 'MST', 'PST', 'CST', 'EST'],
        'availability_percentage': [90.0, 85.0, 100.0, 80.0, 95.0, 90.0, 100.0, 100.0],
        'hire_date': [
            '2020-03-15', '2018-07-22', '2021-01-10', '2019-09-05',
            '2020-11-18', '2019-05-12', '2022-08-01', '2021-06-14'
        ],
        'is_active': [True] * 8
    })

    # Sample projects with detailed history
    sample_projects = pd.DataFrame({
        'project_name': [
            'E-commerce Mobile App', 'AI Analytics Dashboard', 'Corporate Website Redesign',
            'IoT Device Management Platform', 'Healthcare Data Portal'
        ],
        'project_code': ['PROJ001', 'PROJ002', 'PROJ003', 'PROJ004', 'PROJ005'],
        'description': [
            'Cross-platform mobile app for online retail with payment integration',
            'Business intelligence dashboard with ML-driven insights and predictions',
            'Modern responsive website with CMS integration',
            'Cloud platform for managing IoT devices and data streams',
            'HIPAA-compliant portal for patient data management'
        ],
        'client_name': [
            'RetailCorp Inc', 'DataTech Solutions', 'Corporate Services Ltd',
            'SmartDevices Co', 'HealthSystem Partners'
        ],
        'industry': ['E-commerce', 'Analytics', 'Professional Services', 'IoT', 'Healthcare'],
        'project_type': ['mobile_app', 'web_app', 'website', 'platform', 'web_app'],
        'complexity_score': [7, 8, 4, 9, 8],
        'actual_duration_weeks': [24, 16, 8, 32, 20],
        'estimated_duration_weeks': [20, 18, 8, 28, 18],
        'actual_cost': [180000, 120000, 45000, 280000, 160000],
        'estimated_cost': [150000, 130000, 40000, 250000, 140000],
        'team_size': [5, 4, 3, 6, 5],
        'tech_stack_frontend': ['React Native', 'React', 'Next.js', 'React', 'React'],
        'tech_stack_backend': ['FastAPI', 'FastAPI', 'Node.js', 'FastAPI', 'Django'],
        'tech_stack_database': ['PostgreSQL', 'PostgreSQL', 'PostgreSQL', 'PostgreSQL + Redis', 'PostgreSQL'],
        'architecture_pattern': ['microservices', 'layered', 'jamstack', 'microservices', 'layered'],
        'start_date': ['2022-01-15', '2022-08-01', '2023-02-01', '2021-06-01', '2023-03-15'],
        'end_date': ['2022-07-10', '2022-12-15', '2023-04-01', '2022-02-15', '2023-08-10'],
        'delivery_date': ['2022-07-15', '2022-12-10', '2023-03-28', '2022-02-20', '2023-08-15'],
        'on_time_delivery': [False, True, True, False, False],
        'within_budget': [False, True, False, False, False],
        'client_satisfaction': [4.2, 4.8, 4.6, 4.0, 4.5],
        'quality_score': [4.5, 4.7, 4.4, 4.3, 4.6],
        'status': ['completed'] * 5,
        'lessons_learned': [
            'Allocate more time for third-party integrations and app store processes',
            'Early performance testing and incremental ML model deployment',
            'Plan content migration early in the project timeline',
            'IoT device compatibility testing should start early',
            'Healthcare compliance requirements need dedicated resources'
        ]
    })

    # Create samples directory
    samples_dir = 'data/samples'
    os.makedirs(samples_dir, exist_ok=True)

    # Save sample files
    sample_employees.to_excel(f'{samples_dir}/sample_employees.xlsx', index=False)
    sample_projects.to_excel(f'{samples_dir}/sample_projects.xlsx', index=False)

    print(f"Sample Excel files created in {samples_dir}/")

if __name__ == "__main__":
    create_excel_templates()
    create_sample_excel_files()
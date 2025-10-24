"""
Employee Matching Utility
Matches employees from CSV data to required project roles based on skills and availability.
"""

from typing import List, Dict, Any, Optional
from .csv_data_service import CSVDataService
import re


class EmployeeMatcher:
    def __init__(self):
        self.csv_service = CSVDataService()

    def match_employees_to_roles(
        self,
        team_composition: List[Dict[str, Any]],
        required_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Match employees to required roles based on skills and availability.

        Args:
            team_composition: List of required roles from EstimationAgent
            required_skills: List of required technical skills from TechnicalAgent

        Returns:
            Enhanced team_composition with recommended_employees for each role
        """
        # Get available employees with their skills
        available_employees = self.csv_service.get_available_employees()

        if not available_employees:
            # No employee data available, return original composition
            return team_composition

        # Process each role
        enhanced_composition = []
        for role in team_composition:
            role_title = role.get('role', '')
            seniority = role.get('seniority', '')

            # Extract required skills for this role
            role_skills = self._extract_role_skills(role_title, required_skills)

            # Find matching employees
            matched_employees = self._find_matching_employees(
                available_employees,
                role_title,
                seniority,
                role_skills
            )

            # Add top 3 recommendations to the role
            role['recommended_employees'] = matched_employees[:3]
            enhanced_composition.append(role)

        return enhanced_composition

    def _extract_role_skills(self, role_title: str, all_skills: List[str]) -> List[str]:
        """Extract relevant skills for a specific role based on role title."""
        role_lower = role_title.lower()
        relevant_skills = []

        # Define role-to-skill mappings
        role_skill_map = {
            'frontend': ['react', 'vue', 'angular', 'typescript', 'javascript', 'html', 'css', 'next.js', 'tailwind'],
            'backend': ['python', 'node.js', 'java', 'c#', 'go', 'django', 'flask', 'fastapi', 'spring', 'express'],
            'full stack': ['react', 'python', 'node.js', 'typescript', 'javascript', 'django', 'flask', 'express'],
            'mobile': ['react native', 'flutter', 'swift', 'kotlin', 'ios', 'android'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'terraform', 'jenkins'],
            'data': ['python', 'sql', 'pandas', 'numpy', 'spark', 'hadoop', 'tableau'],
            'ai': ['python', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision'],
            'ml': ['python', 'tensorflow', 'pytorch', 'scikit-learn', 'machine learning'],
            'qa': ['selenium', 'cypress', 'jest', 'pytest', 'testing', 'automation'],
            'designer': ['figma', 'sketch', 'adobe xd', 'ui/ux', 'design'],
            'product': ['agile', 'scrum', 'product management', 'jira'],
            'architect': ['system design', 'architecture', 'microservices', 'scalability']
        }

        # Find matching categories
        for category, skills in role_skill_map.items():
            if category in role_lower:
                relevant_skills.extend(skills)

        # Also add any skills from all_skills that match the role
        for skill in all_skills:
            skill_lower = skill.lower()
            for keyword in relevant_skills:
                if keyword in skill_lower or skill_lower in keyword:
                    if skill not in relevant_skills:
                        relevant_skills.append(skill)

        return relevant_skills

    def _find_matching_employees(
        self,
        employees: List[Dict[str, Any]],
        role_title: str,
        seniority: str,
        required_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find and rank employees matching the role requirements.

        Returns list of matched employees with match scores.
        """
        matches = []

        for employee in employees:
            # Calculate match score
            score_data = self._calculate_match_score(
                employee,
                role_title,
                seniority,
                required_skills
            )

            if score_data['match_score'] > 0:
                matches.append({
                    'employee_id': employee.get('employee_id'),
                    'name': employee.get('name'),
                    'title': employee.get('title'),
                    'seniority_level': employee.get('seniority_level'),
                    'hourly_rate': employee.get('hourly_rate'),
                    'availability': f"{employee.get('availability_percentage', 100)}%",
                    'location': employee.get('location'),
                    'match_score': score_data['match_score'],
                    'matching_skills': score_data['matching_skills'],
                    'total_skills': score_data['total_skills'],
                    'match_percentage': score_data['match_percentage']
                })

        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)

        return matches

    def _calculate_match_score(
        self,
        employee: Dict[str, Any],
        role_title: str,
        seniority: str,
        required_skills: List[str]
    ) -> Dict[str, Any]:
        """Calculate how well an employee matches a role."""
        score = 0.0
        matching_skills = []

        employee_skills = employee.get('skills', [])
        employee_title = employee.get('title', '').lower()
        employee_seniority = employee.get('seniority_level', '').lower()

        # 1. Role/Title match (40 points max)
        role_lower = role_title.lower()
        title_keywords = role_lower.split()

        for keyword in title_keywords:
            if len(keyword) > 3:  # Ignore short words like "and", "the"
                if keyword in employee_title:
                    score += 15
                    break

        # 2. Seniority match (20 points max)
        if seniority.lower() == employee_seniority:
            score += 20
        elif self._seniority_compatible(seniority, employee_seniority):
            score += 10

        # 3. Skills match (40 points max)
        if employee_skills and required_skills:
            for emp_skill in employee_skills:
                skill_name = emp_skill.get('skill_name', '').lower()
                proficiency = emp_skill.get('proficiency_level', 0)

                for req_skill in required_skills:
                    if req_skill.lower() in skill_name or skill_name in req_skill.lower():
                        # Weight by proficiency (1-5 scale)
                        skill_score = min(proficiency * 2, 10)  # Max 10 points per skill
                        score += skill_score
                        matching_skills.append({
                            'skill': emp_skill.get('skill_name'),
                            'proficiency': proficiency,
                            'years': emp_skill.get('years_experience', 0)
                        })
                        break

        # Cap total score at 100
        score = min(score, 100)

        # Calculate match percentage
        match_percentage = int(score)

        return {
            'match_score': round(score, 2),
            'matching_skills': matching_skills,
            'total_skills': len(employee_skills),
            'match_percentage': match_percentage
        }

    def _seniority_compatible(self, required: str, employee: str) -> bool:
        """Check if employee seniority is compatible with required seniority."""
        seniority_levels = {
            'junior': 1,
            'mid': 2,
            'mid-level': 2,
            'senior': 3,
            'lead': 4,
            'principal': 5,
            'staff': 5
        }

        req_level = seniority_levels.get(required.lower(), 2)
        emp_level = seniority_levels.get(employee.lower(), 2)

        # Allow +/- 1 level difference
        return abs(req_level - emp_level) <= 1

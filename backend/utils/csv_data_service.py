import pandas as pd
import os
from typing import List, Dict, Any, Optional

class CSVDataService:
    """Service to read historical data from CSV files instead of database"""

    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'samples')
        self.projects_df = None
        self.employees_df = None
        self.employee_skills_df = None
        self._load_data()

    def _load_data(self):
        """Load data from CSV files"""
        try:
            self.projects_df = pd.read_csv(os.path.join(self.base_path, 'sample_projects.csv'))
            self.employees_df = pd.read_csv(os.path.join(self.base_path, 'sample_employees.csv'))
            self.employee_skills_df = pd.read_csv(os.path.join(self.base_path, 'sample_employee_skills.csv'))
            print(f"[OK] Loaded {len(self.projects_df)} projects and {len(self.employees_df)} employees from CSV")
        except Exception as e:
            print(f"[ERROR] Error loading CSV files: {e}")
            self.projects_df = pd.DataFrame()
            self.employees_df = pd.DataFrame()
            self.employee_skills_df = pd.DataFrame()

    def get_similar_projects(self, project_type: str, complexity_score: int, tech_stack: List[str]) -> List[Dict[str, Any]]:
        """Find similar historical projects based on type, complexity, and tech stack"""
        try:
            if self.projects_df.empty:
                return []

            # Filter by project type and complexity
            similar = self.projects_df[
                (self.projects_df['project_type'] == project_type) &
                (self.projects_df['complexity_score'].between(complexity_score - 2, complexity_score + 2)) &
                (self.projects_df['status'] == 'completed')
            ]

            results = []
            for _, project in similar.iterrows():
                # Calculate tech stack similarity
                project_tech = [
                    str(project.get('tech_stack_frontend', '')),
                    str(project.get('tech_stack_backend', '')),
                    str(project.get('tech_stack_database', ''))
                ]

                # Simple similarity check
                tech_similarity = len(set(tech_stack) & set(project_tech)) / max(len(set(tech_stack) | set(project_tech)), 1)

                if tech_similarity > 0.2:  # At least 20% overlap
                    results.append({
                        'project_name': project['project_name'],
                        'project_code': project['project_code'],
                        'complexity_score': int(project['complexity_score']),
                        'actual_duration_weeks': int(project['actual_duration_weeks']),
                        'actual_cost': float(project['actual_cost']),
                        'team_size': int(project['team_size']),
                        'tech_stack': {
                            'frontend': project.get('tech_stack_frontend'),
                            'backend': project.get('tech_stack_backend'),
                            'database': project.get('tech_stack_database')
                        },
                        'on_time_delivery': project['on_time_delivery'],
                        'within_budget': project['within_budget'],
                        'client_satisfaction': float(project['client_satisfaction']),
                        'lessons_learned': project['lessons_learned'],
                        'tech_similarity': tech_similarity
                    })

            # Sort by similarity
            results.sort(key=lambda x: x['tech_similarity'], reverse=True)
            return results[:5]

        except Exception as e:
            print(f"Error finding similar projects: {e}")
            return []

    def get_project_cost_estimates(self, project_type: str, complexity_score: int) -> Dict[str, float]:
        """Get cost estimates based on historical project data"""
        try:
            if self.projects_df.empty:
                return {}

            # Filter similar projects
            similar = self.projects_df[
                (self.projects_df['project_type'] == project_type) &
                (self.projects_df['complexity_score'].between(complexity_score - 2, complexity_score + 2)) &
                (self.projects_df['status'] == 'completed') &
                (self.projects_df['actual_cost'].notna())
            ]

            if similar.empty:
                return {}

            return {
                'avg_cost': float(similar['actual_cost'].mean()),
                'min_cost': float(similar['actual_cost'].min()),
                'max_cost': float(similar['actual_cost'].max()),
                'avg_duration_weeks': float(similar['actual_duration_weeks'].mean()),
                'avg_team_size': float(similar['team_size'].mean()),
                'cost_per_week': float(similar['actual_cost'].mean() / similar['actual_duration_weeks'].mean()),
                'cost_per_team_member': float(similar['actual_cost'].mean() / similar['team_size'].mean()),
                'sample_size': len(similar)
            }

        except Exception as e:
            print(f"Error getting cost estimates: {e}")
            return {}

    def get_team_performance_metrics(self, tech_stack: List[str]) -> Dict[str, Any]:
        """Get performance metrics for employees with relevant skills"""
        try:
            if self.employees_df.empty:
                return {}

            # For now, return basic employee stats
            return {
                'available_employees': len(self.employees_df[self.employees_df['is_active'] == True]),
                'avg_hourly_rate': float(self.employees_df['hourly_rate'].mean()),
                'avg_availability': float(self.employees_df['availability_percentage'].mean()),
                'total_employees': len(self.employees_df)
            }

        except Exception as e:
            print(f"Error getting team metrics: {e}")
            return {}

    def get_risk_indicators(self, project_type: str, complexity_score: int) -> List[Dict[str, Any]]:
        """Get risk indicators based on historical project challenges"""
        try:
            if self.projects_df.empty:
                return []

            # Find projects that had issues
            risky = self.projects_df[
                (self.projects_df['project_type'] == project_type) &
                (self.projects_df['complexity_score'] >= complexity_score - 1) &
                (
                    (self.projects_df['on_time_delivery'] == False) |
                    (self.projects_df['within_budget'] == False) |
                    (self.projects_df['client_satisfaction'] < 4.0)
                )
            ]

            risk_patterns = []
            for _, project in risky.iterrows():
                risks = {
                    'project_name': project['project_name'],
                    'issues': [],
                    'lessons_learned': project['lessons_learned']
                }

                if project['on_time_delivery'] == False:
                    delay_pct = ((project['actual_duration_weeks'] - project['estimated_duration_weeks']) /
                                project['estimated_duration_weeks'] * 100)
                    risks['issues'].append(f"Timeline overrun by {delay_pct:.1f}%")

                if project['within_budget'] == False:
                    cost_overrun = ((project['actual_cost'] - project['estimated_cost']) /
                                   project['estimated_cost'] * 100)
                    risks['issues'].append(f"Budget overrun by {cost_overrun:.1f}%")

                if project['client_satisfaction'] < 4.0:
                    risks['issues'].append(f"Low client satisfaction: {project['client_satisfaction']}/5.0")

                risk_patterns.append(risks)

            return risk_patterns[:5]

        except Exception as e:
            print(f"Error getting risk indicators: {e}")
            return []

    def get_technology_usage_stats(self) -> Dict[str, Any]:
        """Get statistics on technology usage across projects"""
        try:
            if self.projects_df.empty:
                return {}

            tech_columns = ['tech_stack_frontend', 'tech_stack_backend', 'tech_stack_database']
            tech_usage = {}

            for col in tech_columns:
                if col in self.projects_df.columns:
                    value_counts = self.projects_df[col].value_counts()
                    for tech, count in value_counts.items():
                        if pd.notna(tech):
                            tech_usage[str(tech)] = {
                                'count': int(count),
                                'usage_percentage': float(count / len(self.projects_df) * 100)
                            }

            return {
                'total_projects_analyzed': len(self.projects_df),
                'technology_stats': tech_usage
            }

        except Exception as e:
            print(f"Error getting technology stats: {e}")
            return {}

    def get_available_employees(self) -> List[Dict[str, Any]]:
        """Get list of available employees WITH their skills"""
        try:
            if self.employees_df.empty:
                return []

            active_employees = self.employees_df[self.employees_df['is_active'] == True]

            employees_with_skills = []
            for _, row in active_employees.iterrows():
                emp_id = row['employee_id']

                # Get skills for this employee from employee_skills dataframe
                employee_skills = []
                if not self.employee_skills_df.empty:
                    emp_skill_rows = self.employee_skills_df[
                        self.employee_skills_df['employee_id'] == emp_id
                    ]

                    for _, skill_row in emp_skill_rows.iterrows():
                        employee_skills.append({
                            'skill_name': skill_row['skill_name'],
                            'proficiency_level': int(skill_row['proficiency_level']),
                            'years_experience': float(skill_row['years_experience']),
                            'is_primary_skill': skill_row['is_primary_skill'],
                            'certified': skill_row.get('certified', False)
                        })

                employees_with_skills.append({
                    'employee_id': emp_id,
                    'name': row['name'],
                    'email': row['email'],
                    'title': row['title'],
                    'seniority_level': row['seniority_level'],
                    'hourly_rate': float(row['hourly_rate']),
                    'availability_percentage': float(row['availability_percentage']),
                    'department': row['department'],
                    'location': row['location'],
                    'skills': employee_skills  # NOW INCLUDES SKILLS!
                })

            return employees_with_skills

        except Exception as e:
            print(f"Error getting employees: {e}")
            import traceback
            traceback.print_exc()
            return []

    def close(self):
        """Cleanup (not needed for CSV but kept for interface compatibility)"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from ..models.employee_models import Employee, HistoricalProject, ProjectAssignment, EmployeeSkill, Skill
from ..models.database import SessionLocal

class HistoricalDataService:
    def __init__(self):
        self.db = SessionLocal()

    def get_similar_projects(self, project_type: str, complexity_score: int, tech_stack: List[str]) -> List[Dict[str, Any]]:
        """Find similar historical projects based on type, complexity, and tech stack"""
        try:
            # Find projects with similar characteristics
            similar_projects = self.db.query(HistoricalProject).filter(
                and_(
                    HistoricalProject.project_type == project_type,
                    HistoricalProject.complexity_score.between(complexity_score - 2, complexity_score + 2),
                    HistoricalProject.status == 'completed'
                )
            ).all()

            results = []
            for project in similar_projects:
                # Calculate tech stack similarity
                project_tech = []
                if project.tech_stack:
                    project_tech = [
                        project.tech_stack.get('frontend', ''),
                        project.tech_stack.get('backend', ''),
                        project.tech_stack.get('database', ''),
                        project.tech_stack.get('mobile', ''),
                        project.tech_stack.get('ai_ml', '')
                    ]

                tech_similarity = len(set(tech_stack) & set(project_tech)) / len(set(tech_stack) | set(project_tech))

                if tech_similarity > 0.3:  # At least 30% tech stack overlap
                    results.append({
                        'project_name': project.project_name,
                        'project_code': project.project_code,
                        'complexity_score': project.complexity_score,
                        'actual_duration_weeks': project.actual_duration_weeks,
                        'actual_cost': project.actual_cost,
                        'team_size': project.team_size,
                        'tech_stack': project.tech_stack,
                        'on_time_delivery': project.on_time_delivery,
                        'within_budget': project.within_budget,
                        'client_satisfaction': project.client_satisfaction,
                        'lessons_learned': project.lessons_learned,
                        'tech_similarity': tech_similarity
                    })

            # Sort by similarity and return top 5
            results.sort(key=lambda x: x['tech_similarity'], reverse=True)
            return results[:5]

        except Exception as e:
            print(f"Error finding similar projects: {e}")
            return []

    def get_team_performance_metrics(self, required_skills: List[str]) -> Dict[str, Any]:
        """Get performance metrics for employees with required skills"""
        try:
            # Find employees with required skills
            skilled_employees = self.db.query(Employee).join(EmployeeSkill).join(Skill).filter(
                and_(
                    Skill.name.in_(required_skills),
                    Employee.is_active == True,
                    EmployeeSkill.proficiency_level >= 3
                )
            ).all()

            if not skilled_employees:
                return {}

            employee_ids = [emp.id for emp in skilled_employees]

            # Get their project assignment history
            assignments = self.db.query(ProjectAssignment).filter(
                ProjectAssignment.employee_id.in_(employee_ids)
            ).all()

            # Calculate metrics
            total_assignments = len(assignments)
            avg_performance = sum(a.performance_rating for a in assignments if a.performance_rating) / total_assignments if total_assignments > 0 else 0
            avg_hourly_rate = sum(a.hourly_rate_at_time for a in assignments if a.hourly_rate_at_time) / total_assignments if total_assignments > 0 else 0

            # Group by role
            role_metrics = {}
            for assignment in assignments:
                role = assignment.role_in_project
                if role not in role_metrics:
                    role_metrics[role] = {
                        'count': 0,
                        'avg_performance': 0,
                        'avg_rate': 0,
                        'total_performance': 0,
                        'total_rate': 0
                    }

                role_metrics[role]['count'] += 1
                if assignment.performance_rating:
                    role_metrics[role]['total_performance'] += assignment.performance_rating
                if assignment.hourly_rate_at_time:
                    role_metrics[role]['total_rate'] += assignment.hourly_rate_at_time

            # Calculate averages
            for role, metrics in role_metrics.items():
                if metrics['count'] > 0:
                    metrics['avg_performance'] = metrics['total_performance'] / metrics['count']
                    metrics['avg_rate'] = metrics['total_rate'] / metrics['count']

            return {
                'available_employees': len(skilled_employees),
                'total_assignments': total_assignments,
                'avg_performance_rating': avg_performance,
                'avg_hourly_rate': avg_hourly_rate,
                'role_metrics': role_metrics,
                'skilled_employees': [
                    {
                        'name': emp.name,
                        'title': emp.title,
                        'seniority_level': emp.seniority_level,
                        'hourly_rate': emp.hourly_rate,
                        'availability_percentage': emp.availability_percentage
                    } for emp in skilled_employees
                ]
            }

        except Exception as e:
            print(f"Error getting team performance metrics: {e}")
            return {}

    def get_project_cost_estimates(self, project_type: str, complexity_score: int) -> Dict[str, float]:
        """Get cost estimates based on historical project data"""
        try:
            # Find similar projects for cost analysis
            similar_projects = self.db.query(HistoricalProject).filter(
                and_(
                    HistoricalProject.project_type == project_type,
                    HistoricalProject.complexity_score.between(complexity_score - 2, complexity_score + 2),
                    HistoricalProject.status == 'completed',
                    HistoricalProject.actual_cost.isnot(None)
                )
            ).all()

            if not similar_projects:
                return {}

            costs = [p.actual_cost for p in similar_projects]
            durations = [p.actual_duration_weeks for p in similar_projects]
            team_sizes = [p.team_size for p in similar_projects]

            # Calculate statistics
            avg_cost = sum(costs) / len(costs)
            min_cost = min(costs)
            max_cost = max(costs)
            avg_duration = sum(durations) / len(durations)
            avg_team_size = sum(team_sizes) / len(team_sizes)

            # Calculate cost per week and per team member
            cost_per_week = avg_cost / avg_duration if avg_duration > 0 else 0
            cost_per_team_member = avg_cost / avg_team_size if avg_team_size > 0 else 0

            return {
                'avg_cost': avg_cost,
                'min_cost': min_cost,
                'max_cost': max_cost,
                'avg_duration_weeks': avg_duration,
                'avg_team_size': avg_team_size,
                'cost_per_week': cost_per_week,
                'cost_per_team_member': cost_per_team_member,
                'sample_size': len(similar_projects)
            }

        except Exception as e:
            print(f"Error getting cost estimates: {e}")
            return {}

    def get_technology_usage_stats(self) -> Dict[str, Any]:
        """Get statistics on technology usage across projects"""
        try:
            projects = self.db.query(HistoricalProject).filter(
                HistoricalProject.tech_stack.isnot(None)
            ).all()

            tech_usage = {}
            total_projects = len(projects)

            for project in projects:
                if project.tech_stack:
                    for category, tech in project.tech_stack.items():
                        if tech:
                            if tech not in tech_usage:
                                tech_usage[tech] = {
                                    'count': 0,
                                    'avg_satisfaction': 0,
                                    'avg_quality': 0,
                                    'success_rate': 0,
                                    'projects': []
                                }

                            tech_usage[tech]['count'] += 1
                            tech_usage[tech]['projects'].append({
                                'name': project.project_name,
                                'satisfaction': project.client_satisfaction,
                                'quality': project.quality_score,
                                'on_time': project.on_time_delivery,
                                'on_budget': project.within_budget
                            })

            # Calculate averages and success rates
            for tech, stats in tech_usage.items():
                projects_with_tech = stats['projects']
                if projects_with_tech:
                    stats['avg_satisfaction'] = sum(p['satisfaction'] for p in projects_with_tech if p['satisfaction']) / len(projects_with_tech)
                    stats['avg_quality'] = sum(p['quality'] for p in projects_with_tech if p['quality']) / len(projects_with_tech)
                    stats['success_rate'] = sum(1 for p in projects_with_tech if p['on_time'] and p['on_budget']) / len(projects_with_tech)
                    stats['usage_percentage'] = (stats['count'] / total_projects) * 100

            return {
                'total_projects_analyzed': total_projects,
                'technology_stats': tech_usage
            }

        except Exception as e:
            print(f"Error getting technology usage stats: {e}")
            return {}

    def get_risk_indicators(self, project_type: str, complexity_score: int) -> List[Dict[str, Any]]:
        """Get risk indicators based on historical project challenges"""
        try:
            # Find projects with similar characteristics that had issues
            risky_projects = self.db.query(HistoricalProject).filter(
                and_(
                    HistoricalProject.project_type == project_type,
                    HistoricalProject.complexity_score >= complexity_score - 1,
                    or_(
                        HistoricalProject.on_time_delivery == False,
                        HistoricalProject.within_budget == False,
                        HistoricalProject.client_satisfaction < 4.0
                    )
                )
            ).all()

            risk_patterns = []
            for project in risky_projects:
                risks = {
                    'project_name': project.project_name,
                    'issues': [],
                    'lessons_learned': project.lessons_learned
                }

                if not project.on_time_delivery:
                    delay_percentage = ((project.actual_duration_weeks - project.estimated_duration_weeks) / project.estimated_duration_weeks) * 100 if project.estimated_duration_weeks else 0
                    risks['issues'].append(f"Timeline overrun by {delay_percentage:.1f}%")

                if not project.within_budget:
                    cost_overrun = ((project.actual_cost - project.estimated_cost) / project.estimated_cost) * 100 if project.estimated_cost else 0
                    risks['issues'].append(f"Budget overrun by {cost_overrun:.1f}%")

                if project.client_satisfaction and project.client_satisfaction < 4.0:
                    risks['issues'].append(f"Low client satisfaction: {project.client_satisfaction}/5.0")

                if project.challenges_faced:
                    risks['common_challenges'] = project.challenges_faced

                risk_patterns.append(risks)

            return risk_patterns

        except Exception as e:
            print(f"Error getting risk indicators: {e}")
            return []

    def close(self):
        """Close database connection"""
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
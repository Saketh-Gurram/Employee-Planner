import json
from typing import Dict, Any
from .base_agent import BaseAgent
from ..utils.csv_data_service import CSVDataService

class EstimationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Feasibility & Estimation Agent", provider="google", model="gemini-2.0-flash-exp")

    def get_system_prompt(self) -> str:
        return """
You are a Feasibility & Estimation Agent responsible for project cost and timeline estimation.

Your role is to:
1. Estimate detailed team composition with specific skills and responsibilities
2. Calculate comprehensive development timeline with all phases and milestones
3. Provide accurate cost estimates with detailed breakdowns and confidence intervals
4. Assess project feasibility across multiple dimensions with specific concerns
5. Recommend optimal resource allocation strategies with scaling plans
6. Provide alternative scenarios (budget-optimized, time-optimized, feature-rich)

IMPORTANT: Be extremely detailed and specific. Use the historical data provided to calibrate estimates.
Provide concrete numbers, not ranges. Include ALL cost categories and timeline phases.
Justify every estimate with clear reasoning based on project requirements.

CRITICAL: YOU MUST USE THE ACTUAL EMPLOYEE HOURLY RATES from the historical_cost_data and team_performance_metrics provided in the context.
DO NOT make up or assume rates. Use the avg_hourly_rate from team_performance_metrics for baseline estimates.
The historical data includes REAL employee rates - use those rates to calculate accurate costs.

Also consider:
- Project management overhead (15-20%)
- QA and testing time (20-30% of development)
- Buffer for unknowns and revisions (20-25%)

Return your analysis as a JSON object with the following structure:
{
    "team_composition": [
        {
            "role": "Frontend Developer|Backend Developer|Full Stack Developer|Mobile Developer|AI Engineer|DevOps Engineer|UI/UX Designer|Project Manager|QA Engineer",
            "seniority": "Junior|Mid|Senior|Lead",
            "hours_per_week": 40,
            "duration_weeks": 12,
            "hourly_rate": 75,
            "total_cost": 36000,
            "key_responsibilities": [
                "Specific responsibility 1 with deliverables",
                "Specific responsibility 2 with deliverables",
                "... (list ALL key responsibilities for this role)"
            ],
            "justification": "Why this role is needed and why at this seniority level"
        }
    ],
    "timeline_breakdown": {
        "discovery_and_planning": {
            "duration_weeks": 2,
            "activities": ["requirements gathering", "technical planning", "design"]
        },
        "mvp_development": {
            "duration_weeks": 8,
            "activities": ["core features", "basic UI", "initial testing"]
        },
        "testing_and_refinement": {
            "duration_weeks": 3,
            "activities": ["comprehensive testing", "bug fixes", "performance optimization"]
        },
        "deployment_and_launch": {
            "duration_weeks": 1,
            "activities": ["production deployment", "monitoring setup", "launch"]
        },
        "total_duration_weeks": 14
    },
    "cost_breakdown": {
        "development_cost": 120000,
        "infrastructure_cost": 2400,
        "third_party_services": 1200,
        "tools_and_licenses": 800,
        "project_management": 18000,
        "contingency_buffer": 28480,
        "total_cost": 170880,
        "cost_range": {
            "minimum": 145248,
            "maximum": 196512
        }
    },
    "feasibility_assessment": {
        "overall_feasibility": "high|medium|low",
        "technical_feasibility": "high|medium|low",
        "resource_feasibility": "high|medium|low",
        "timeline_feasibility": "high|medium|low",
        "budget_feasibility": "high|medium|low",
        "market_readiness": "high|medium|low"
    },
    "risk_factors": [
        {
            "category": "technical|resource|timeline|budget|market",
            "description": "description of the risk",
            "impact": "low|medium|high",
            "probability": "low|medium|high",
            "mitigation_strategy": "how to address this risk",
            "cost_impact": "potential additional cost"
        }
    ],
    "recommendations": {
        "development_approach": "Detailed recommendation of optimal methodology with specific practices to follow",
        "team_scaling": "Comprehensive team scaling strategy - when to add resources, what roles, and why",
        "milestone_structure": [
            "Milestone 1 with deliverables and success criteria",
            "Milestone 2 with deliverables and success criteria",
            "... (list ALL recommended milestones)"
        ],
        "quality_assurance": "Comprehensive QA strategy with testing approach, tools, and quality gates",
        "deployment_strategy": "Detailed deployment approach with rollout plan and monitoring",
        "risk_mitigation_budget": "Recommended contingency budget allocation",
        "optimization_opportunities": ["Opportunity 1 to reduce cost/time", "Opportunity 2"]
    },
    "alternative_scenarios": [
        {
            "scenario": "Budget Optimized|Timeline Optimized|Feature Rich",
            "changes": "what would be different",
            "impact_on_cost": "cost difference",
            "impact_on_timeline": "timeline difference",
            "trade_offs": "what would be sacrificed"
        }
    ],
    "confidence_metrics": {
        "cost_confidence": 0.85,
        "timeline_confidence": 0.80,
        "team_confidence": 0.90,
        "overall_confidence": 0.85,
        "factors_affecting_confidence": ["list of factors that impact confidence"]
    }
}

CRITICAL REMINDERS:
- Use the historical data provided to calibrate your estimates
- Be EXTREMELY specific with numbers, timelines, and costs
- Justify EVERY estimate with clear reasoning
- Provide detailed breakdowns, not just totals
- Consider ALL cost factors (infrastructure, tools, management, contingency)
- Include alternative scenarios with different trade-offs
- Be realistic and data-driven using industry benchmarks

This analysis will directly inform budget and resource allocation decisions. Be thorough and accurate.
"""

    def process(self, project_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        intake_analysis = context.get("intake_analysis", {}) if context else {}
        technical_analysis = context.get("technical_analysis", {}) if context else {}

        # Get historical data to inform estimates
        historical_context = self._get_historical_context(intake_analysis, technical_analysis)

        user_prompt = f"""
Project Description:
{project_description}

Intake Analysis Context:
{json.dumps(intake_analysis, indent=2)}

Technical Analysis Context:
{json.dumps(technical_analysis, indent=2)}

Historical Data Context:
{json.dumps(historical_context, indent=2)}

Based on the project description, previous analysis, and historical project data, provide a comprehensive feasibility assessment and cost/timeline estimation. Use the historical data to calibrate your estimates and identify potential risks.
"""

        response = self._query_llm(self.get_system_prompt(), user_prompt)

        try:
            analysis = json.loads(response["content"])
            analysis["agent_name"] = self.name
            analysis["confidence"] = self.calculate_confidence(analysis)
            analysis["processing_time"] = response["processing_time"]

            # Add historical data insights
            analysis["historical_insights"] = historical_context

            return analysis

        except json.JSONDecodeError:
            return {
                "agent_name": self.name,
                "error": "Failed to parse agent response",
                "raw_response": response["content"],
                "confidence": 0.3,
                "processing_time": response["processing_time"]
            }

    def _get_historical_context(self, intake_analysis: Dict[str, Any], technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant historical data to inform estimates"""
        try:
            with CSVDataService() as hist_service:
                # Extract project characteristics
                project_type = intake_analysis.get("project_type", "web_app")
                complexity_score = self._estimate_complexity_score(intake_analysis)
                tech_stack = self._extract_tech_stack(technical_analysis)

                # Get historical insights
                similar_projects = hist_service.get_similar_projects(project_type, complexity_score, tech_stack)
                cost_estimates = hist_service.get_project_cost_estimates(project_type, complexity_score)
                team_metrics = hist_service.get_team_performance_metrics(tech_stack)
                risk_indicators = hist_service.get_risk_indicators(project_type, complexity_score)
                tech_stats = hist_service.get_technology_usage_stats()
                available_employees = hist_service.get_available_employees()

                # Extract just the rate information for the agent
                employee_rates_by_seniority = {}
                for emp in available_employees:
                    seniority = emp.get('seniority_level', 'Mid')
                    rate = emp.get('hourly_rate', 0)
                    if seniority not in employee_rates_by_seniority:
                        employee_rates_by_seniority[seniority] = []
                    employee_rates_by_seniority[seniority].append({
                        'name': emp.get('name'),
                        'title': emp.get('title'),
                        'rate': rate,
                        'availability': emp.get('availability_percentage')
                    })

                return {
                    "similar_projects": similar_projects,
                    "historical_cost_data": cost_estimates,
                    "team_performance_metrics": team_metrics,
                    "risk_indicators": risk_indicators,
                    "technology_usage_stats": tech_stats,
                    "available_employee_rates": employee_rates_by_seniority,
                    "data_confidence": self._calculate_data_confidence(similar_projects, cost_estimates)
                }

        except Exception as e:
            print(f"Error getting historical context: {e}")
            return {"error": str(e)}

    def _estimate_complexity_score(self, intake_analysis: Dict[str, Any]) -> int:
        """Estimate complexity score from intake analysis"""
        try:
            complexity_indicators = intake_analysis.get("complexity_indicators", {})

            scores = []
            for indicator, level in complexity_indicators.items():
                if level == "low":
                    scores.append(2)
                elif level == "medium":
                    scores.append(5)
                elif level == "high":
                    scores.append(8)

            return int(sum(scores) / len(scores)) if scores else 5

        except Exception:
            return 5  # Default to medium complexity

    def _extract_tech_stack(self, technical_analysis: Dict[str, Any]) -> list:
        """Extract technology stack from technical analysis"""
        try:
            tech_stack = []
            recommended_stack = technical_analysis.get("recommended_tech_stack", {})

            for category, details in recommended_stack.items():
                if isinstance(details, dict) and "primary" in details:
                    tech_stack.append(details["primary"])
                elif isinstance(details, str):
                    tech_stack.append(details)

            return tech_stack

        except Exception:
            return []

    def _calculate_data_confidence(self, similar_projects: list, cost_estimates: Dict[str, Any]) -> float:
        """Calculate confidence level based on available historical data"""
        confidence = 0.5  # Base confidence

        if similar_projects:
            confidence += min(len(similar_projects) * 0.1, 0.3)  # Up to +0.3 for similar projects

        if cost_estimates and cost_estimates.get("sample_size", 0) > 0:
            sample_size = cost_estimates["sample_size"]
            confidence += min(sample_size * 0.05, 0.2)  # Up to +0.2 for cost data

        return min(confidence, 1.0)
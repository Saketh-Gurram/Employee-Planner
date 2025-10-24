import asyncio
from typing import Dict, Any, List
from .intake_agent import IntakeAgent
from .technical_agent import TechnicalAgent
from .estimation_agent import EstimationAgent
from .summary_agent import SummaryAgent
from ..utils.logger import get_logger
from ..utils.employee_matcher import EmployeeMatcher

logger = get_logger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.technical_agent = TechnicalAgent()
        self.estimation_agent = EstimationAgent()
        self.summary_agent = SummaryAgent()
        self.employee_matcher = EmployeeMatcher()

    async def analyze_project(self, project_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Orchestrates the multi-agent analysis of a project description.
        """
        logger.info(f"Starting project analysis for: {project_description[:100]}...")

        try:
            # Step 1: Project Intake Analysis
            logger.info("Running intake agent...")
            intake_result = await self._run_agent_async(
                self.intake_agent,
                project_description,
                context
            )

            # Step 2: Technical Analysis
            logger.info("Running technical agent...")
            technical_context = {
                **(context or {}),
                "intake_analysis": intake_result
            }
            technical_result = await self._run_agent_async(
                self.technical_agent,
                project_description,
                technical_context
            )

            # Step 3: Estimation Analysis
            logger.info("Running estimation agent...")
            estimation_context = {
                **(context or {}),
                "intake_analysis": intake_result,
                "technical_analysis": technical_result
            }
            estimation_result = await self._run_agent_async(
                self.estimation_agent,
                project_description,
                estimation_context
            )

            # Step 3.5: Employee Matching (enhance team composition with employee recommendations)
            logger.info("Matching employees to required roles...")
            try:
                team_composition = estimation_result.get('team_composition', [])
                required_skills = self._extract_required_skills(technical_result)

                logger.info(f"[DEBUG] Team composition has {len(team_composition)} roles")
                logger.info(f"[DEBUG] Required skills: {required_skills}")

                if team_composition:
                    enhanced_team = self.employee_matcher.match_employees_to_roles(
                        team_composition,
                        required_skills
                    )

                    # Count how many employees were matched
                    total_matched = sum(len(role.get('recommended_employees', [])) for role in enhanced_team)
                    logger.info(f"[DEBUG] Employee matching completed: {len(enhanced_team)} roles, {total_matched} total employee matches")

                    # Log first role's employees for debugging
                    if enhanced_team and enhanced_team[0].get('recommended_employees'):
                        first_emp = enhanced_team[0]['recommended_employees'][0]
                        logger.info(f"[DEBUG] First match: {first_emp.get('name')} for role {enhanced_team[0].get('role')}")

                    estimation_result['team_composition'] = enhanced_team
                else:
                    logger.warning("[DEBUG] No team_composition found in estimation_result!")
            except Exception as e:
                logger.error(f"Employee matching failed: {str(e)}. Continuing without employee recommendations.")
                import traceback
                logger.error(traceback.format_exc())

            # Step 4: Summary Generation
            logger.info("Running summary agent...")
            summary_context = {
                **(context or {}),
                "intake_analysis": intake_result,
                "technical_analysis": technical_result,
                "estimation_analysis": estimation_result
            }
            summary_result = await self._run_agent_async(
                self.summary_agent,
                project_description,
                summary_context
            )

            # Compile final analysis
            final_analysis = {
                "input_description": project_description,
                "intake_analysis": intake_result,
                "technical_analysis": technical_result,
                "estimation_analysis": estimation_result,
                "summary": summary_result,
                "overall_confidence": self._calculate_overall_confidence([
                    intake_result, technical_result, estimation_result, summary_result
                ])
            }

            logger.info("Project analysis completed successfully")
            return final_analysis

        except Exception as e:
            logger.error(f"Error in project analysis: {str(e)}")
            raise

    async def _run_agent_async(self, agent, project_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an agent asynchronously.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, agent.process, project_description, context)

    def _calculate_overall_confidence(self, agent_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confidence score from all agent results.
        """
        confidences = []
        for result in agent_results:
            if isinstance(result, dict) and "confidence" in result:
                confidences.append(result["confidence"])

        if not confidences:
            return 0.5

        # Weighted average with higher weight on later agents
        weights = [1, 1.2, 1.5, 1.3][:len(confidences)]
        weighted_sum = sum(conf * weight for conf, weight in zip(confidences, weights))
        total_weight = sum(weights)

        return min(weighted_sum / total_weight, 1.0)

    def _extract_required_skills(self, technical_result: Dict[str, Any]) -> List[str]:
        """
        Extract list of required skills from technical analysis.
        """
        skills = []

        # Extract from recommended tech stack
        tech_stack = technical_result.get('recommended_tech_stack', {})
        for category, details in tech_stack.items():
            if isinstance(details, dict):
                if 'primary' in details:
                    skills.append(details['primary'])
                if 'ui_framework' in details:
                    skills.append(details['ui_framework'])
                if 'state_management' in details:
                    skills.append(details['state_management'])
            elif isinstance(details, str):
                skills.append(details)

        # Extract from third-party APIs
        integration_reqs = technical_result.get('integration_requirements', {})
        if 'third_party_apis' in integration_reqs:
            apis = integration_reqs['third_party_apis']
            if isinstance(apis, list):
                skills.extend(apis)

        return skills
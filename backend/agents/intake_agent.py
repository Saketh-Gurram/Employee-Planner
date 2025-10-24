import json
from typing import Dict, Any
from .base_agent import BaseAgent

class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Project Intake Agent", provider="google", model="gemini-2.0-flash-exp")

    def get_system_prompt(self) -> str:
        return """
You are a Project Intake Agent, the first step in analyzing project feasibility.

Your role is to:
1. Parse and understand the project description thoroughly
2. Extract ALL key features and goals mentioned or implied
3. Identify the core problem being solved and its significance
4. Classify the project type and domain accurately
5. Extract any mentioned constraints or requirements with details
6. Identify potential user personas and use cases
7. Assess the business value and market opportunity

IMPORTANT: Be extremely detailed and comprehensive. Extract every piece of relevant information.
Do NOT provide generic responses. Tailor your analysis to the specific project described.

Return your analysis as a JSON object with the following structure:
{
    "project_summary": "Detailed 3-5 sentence summary explaining what the project aims to achieve, why it matters, and who benefits",
    "project_type": "web_app|mobile_app|desktop_app|api|ai_ml|data_analytics|other",
    "domain": "e-commerce|healthcare|finance|education|entertainment|productivity|other",
    "core_features": [
        "Feature 1 with specific details about what it does",
        "Feature 2 with specific details about what it does",
        "Feature 3 with specific details about what it does",
        "... (list ALL features mentioned or implied, be comprehensive)"
    ],
    "target_users": "Detailed description of who will use this product, including demographics, use cases, and specific needs they have",
    "user_personas": [
        {
            "persona_name": "Primary User Type",
            "description": "Detailed description of this user type",
            "needs": ["specific need 1", "specific need 2"],
            "pain_points": ["pain point 1", "pain point 2"]
        }
    ],
    "key_requirements": {
        "functional": [
            "Detailed functional requirement 1 with specifics",
            "Detailed functional requirement 2 with specifics",
            "... (be thorough, include all implied requirements)"
        ],
        "non_functional": [
            "Specific performance requirement (e.g., 'Response time under 200ms')",
            "Specific security requirement (e.g., 'HIPAA compliance for health data')",
            "Specific scalability requirement (e.g., 'Support 100k concurrent users')",
            "... (include ALL implied non-functional requirements)"
        ]
    },
    "mentioned_constraints": {
        "budget": "Specific budget details if mentioned, or analysis of implied budget level",
        "timeline": "Specific timeline details if mentioned, or analysis of urgency indicators",
        "technology": "Specific tech requirements or preferences mentioned",
        "team": "Team size or expertise requirements mentioned",
        "compliance": "Any regulatory or compliance requirements (GDPR, HIPAA, SOC2, etc.)"
    },
    "complexity_indicators": {
        "data_complexity": "low|medium|high - with detailed reasoning why",
        "integration_complexity": "low|medium|high - with detailed reasoning and list of integrations",
        "user_interface_complexity": "low|medium|high - with detailed reasoning about UI needs",
        "business_logic_complexity": "low|medium|high - with detailed reasoning about logic complexity",
        "overall_complexity_summary": "2-3 sentences explaining the overall project complexity"
    },
    "business_value": {
        "problem_being_solved": "Detailed description of the problem",
        "market_opportunity": "Assessment of market potential and opportunity size",
        "competitive_advantages": ["Unique aspect 1", "Unique aspect 2"],
        "success_metrics": ["Key metric 1 that defines success", "Key metric 2"]
    },
    "technical_considerations": [
        "Important technical consideration 1",
        "Important technical consideration 2",
        "... (list all relevant technical aspects to consider)"
    ],
    "questions_for_clarification": [
        "Specific question 1 to better understand requirements",
        "Specific question 2 to clarify ambiguities",
        "... (ask 5-10 insightful questions)"
    ]
}

Be thorough, specific, and detailed. This analysis will guide all downstream decisions.
Focus on extracting EVERY piece of relevant information from the project description.
"""

    def process(self, project_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        user_prompt = f"""
Project Description:
{project_description}

Additional Context:
{json.dumps(context or {}, indent=2)}

Please analyze this project description and provide a comprehensive intake analysis.
"""

        response = self._query_llm(self.get_system_prompt(), user_prompt)

        try:
            # Parse the JSON response
            analysis = json.loads(response["content"])

            # Add metadata
            analysis["agent_name"] = self.name
            analysis["confidence"] = self.calculate_confidence(analysis)
            analysis["processing_time"] = response["processing_time"]

            return analysis

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "agent_name": self.name,
                "error": "Failed to parse agent response",
                "raw_response": response["content"],
                "confidence": 0.3,
                "processing_time": response["processing_time"]
            }
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import time
import os
import re
from dotenv import load_dotenv
from ..utils.llm_config import get_llm_client

load_dotenv()

class BaseAgent(ABC):
    def __init__(self, name: str, provider: str = "google", model: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.provider = provider
        self.model = model

        # Initialize LLM using the configuration utility
        self.llm = get_llm_client(provider=provider, model=model)

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def process(self, project_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass

    def _strip_markdown_wrapper(self, content: str) -> str:
        """Remove markdown code block wrapper from LLM response if present."""
        # Remove ```json ... ``` or ``` ... ``` wrapper
        content = content.strip()
        if content.startswith("```"):
            # Remove opening ```json or ```
            content = re.sub(r'^```(?:json)?\s*\n', '', content)
            # Remove closing ```
            content = re.sub(r'\n```\s*$', '', content)
        return content.strip()

    def _query_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        start_time = time.time()
        try:
            response = self.llm.invoke(messages)
            processing_time = time.time() - start_time

            # Strip markdown wrapper if present
            clean_content = self._strip_markdown_wrapper(response.content)

            return {
                "content": clean_content,
                "processing_time": processing_time
            }
        except Exception as e:
            error_str = str(e)

            # Check if it's a quota/rate limit error
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                raise Exception("🤖 Our AI assistant is taking a power nap right now! ⚡ It's been working hard and needs to recharge. Please try again in a few moments, or contact support if this persists.")

            # Re-raise other errors
            raise

    def calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        confidence_factors = {
            "detail_level": min(len(str(analysis).split()) / 100, 1.0),
            "specific_recommendations": 0.8 if "specific" in str(analysis).lower() else 0.6,
            "risk_awareness": 0.9 if "risk" in str(analysis).lower() else 0.7
        }

        return sum(confidence_factors.values()) / len(confidence_factors)
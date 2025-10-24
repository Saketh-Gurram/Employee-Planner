from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..utils.llm_config import get_available_providers, test_llm_connection
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers based on configured API keys"""
    try:
        providers = get_available_providers()

        if not providers:
            return {
                "providers": [],
                "message": "No LLM providers configured. Please add API keys to environment variables.",
                "setup_instructions": {
                    "google": "Get API key from: https://makersuite.google.com/app/apikey",
                    "openai": "Get API key from: https://platform.openai.com/api-keys",
                    "anthropic": "Get API key from: https://console.anthropic.com/"
                }
            }

        return {
            "providers": providers,
            "current_default": "google",
            "message": f"Found {len(providers)} configured LLM provider(s)"
        }

    except Exception as e:
        logger.error(f"Error getting LLM providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/test/{provider}")
async def test_llm_provider(provider: str):
    """Test connection to a specific LLM provider"""
    try:
        result = test_llm_connection(provider)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return {
            "success": True,
            "provider": provider,
            "message": result["message"],
            "response_preview": result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing LLM provider {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/test-all")
async def test_all_llm_providers():
    """Test all configured LLM providers"""
    try:
        providers = get_available_providers()
        results = []

        for provider in providers:
            result = test_llm_connection(provider["name"])
            results.append({
                "provider": provider["name"],
                "display_name": provider["display_name"],
                "success": result["success"],
                "message": result["message"]
            })

        successful_providers = [r for r in results if r["success"]]

        return {
            "results": results,
            "summary": {
                "total_tested": len(results),
                "successful": len(successful_providers),
                "failed": len(results) - len(successful_providers)
            },
            "recommendation": "Use Google Gemini for best cost/performance ratio" if any(r["provider"] == "google" and r["success"] for r in results) else "Configure Google API key for optimal performance"
        }

    except Exception as e:
        logger.error(f"Error testing all LLM providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
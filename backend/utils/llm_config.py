import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Note: OpenAI and Anthropic imports are optional - only import if needed
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

load_dotenv()

def get_llm_client(provider: Optional[str] = None, model: Optional[str] = None):
    """
    Get LLM client based on provider and model.

    Args:
        provider: 'google', 'openai', 'anthropic' (defaults to 'google')
        model: Specific model name (uses provider defaults if not specified)

    Returns:
        Configured LLM client
    """

    # Default to Google Gemini
    if not provider:
        provider = os.getenv("DEFAULT_LLM_PROVIDER", "google")

    if provider.lower() == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for Google provider")

        model = model or "gemini-2.0-flash-exp"

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.1,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )

    elif provider.lower() == "openai":
        if ChatOpenAI is None:
            raise ImportError("langchain-openai package is required for OpenAI provider. Install with: pip install langchain-openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")

        model = model or "gpt-4"

        return ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=api_key
        )

    elif provider.lower() == "anthropic":
        if ChatAnthropic is None:
            raise ImportError("langchain-anthropic package is required for Anthropic provider. Install with: pip install langchain-anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider")

        model = model or "claude-3-sonnet-20240229"

        return ChatAnthropic(
            model=model,
            temperature=0.1,
            api_key=api_key
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def get_available_providers():
    """Get list of available LLM providers based on configured API keys"""
    providers = []

    if os.getenv("GOOGLE_API_KEY"):
        providers.append({
            "name": "google",
            "display_name": "Google Gemini",
            "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            "recommended": True
        })

    if os.getenv("OPENAI_API_KEY"):
        providers.append({
            "name": "openai",
            "display_name": "OpenAI",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "recommended": False
        })

    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append({
            "name": "anthropic",
            "display_name": "Anthropic Claude",
            "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "recommended": False
        })

    return providers

def test_llm_connection(provider: str = "google"):
    """Test LLM connection with a simple query"""
    try:
        llm = get_llm_client(provider)

        from langchain_core.messages import HumanMessage

        test_message = HumanMessage(content="Hello! Please respond with 'Connection successful' to confirm the API is working.")
        response = llm.invoke([test_message])

        return {
            "success": True,
            "provider": provider,
            "response": response.content,
            "message": f"{provider.title()} LLM connection successful"
        }

    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "error": str(e),
            "message": f"Failed to connect to {provider.title()} LLM: {str(e)}"
        }
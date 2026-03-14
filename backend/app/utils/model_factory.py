"""
Model factory utility for creating LLM instances.
"""

import os
from typing import Optional, Union, Any
from app.config.settings import Settings

# --- Agno Model Classes ---
from agno.models.google import Gemini as AgnoGemini
from agno.models.openai import OpenAIChat as AgnoOpenAI
from agno.models.anthropic import Claude as AgnoClaude
from agno.models.groq import Groq as AgnoGroq

# --- Browser-Use Model Classes ---
from browser_use import ChatGoogle
from browser_use import ChatOpenAI
from browser_use import ChatAnthropic
from browser_use import ChatGroq

try:
    from agno.models.ollama import Ollama as AgnoOllama
    from browser_use import ChatOllama
    _ollama_available = True
except ImportError:
    _ollama_available = False

SUPPORTED_MODELS = {
    "Google": {
        "api_key_env": "GOOGLE_API_KEY",
        "models": {
            "gemini-2.5-flash": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
            "gemini-2.0-flash": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
            "gemini-2.5-pro": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
        },
    },
    "OpenAI": {
        "api_key_env": "OPENAI_API_KEY",
        "models": {
            "gpt-4o": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
            "gpt-4o-mini": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
            "o3": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
        },
    },
    "Anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "models": {
            "claude-3-7-sonnet-latest": {"agno_class": AgnoClaude, "browser_use_class": ChatAnthropic, "param_name": "id"},
            "claude-sonnet-4-0": {"agno_class": AgnoClaude, "browser_use_class": ChatAnthropic, "param_name": "id"},
        },
    },
    "Groq": {
        "api_key_env": "GROQ_API_KEY",
        "models": {
            "meta-llama/llama-4-maverick-17b-128e-instruct": {"agno_class": AgnoGroq, "browser_use_class": ChatGroq, "param_name": "id"},
            "meta-llama/llama-3.1-8b-instant": {"agno_class": AgnoGroq, "browser_use_class": ChatGroq, "param_name": "id"},
        },
    },
    "Ollama": {
        "api_key_env": None,  # No API key needed
        "models": {
            "llama3.2": {"agno_class": None, "browser_use_class": None, "param_name": "id"},
            "gemma3": {"agno_class": None, "browser_use_class": None, "param_name": "id"},
            "qwen2.5": {"agno_class": None, "browser_use_class": None, "param_name": "id"},
            "codellama": {"agno_class": None, "browser_use_class": None, "param_name": "id"},
            "mistral": {"agno_class": None, "browser_use_class": None, "param_name": "id"},
        },
    },
}

def get_llm_instance(provider: str, model_name: str, for_agno: bool = True) -> Optional[Union[object, Any]]:
    """
    Factory function to get an instance of an LLM provider.

    Args:
        provider (str): The LLM provider (e.g., 'Google', 'OpenAI').
        model_name (str): The specific model name (e.g., 'gemini-2.5-flash').
        for_agno (bool): True to get the agno-native class, False for the browser-use class.

    Returns:
        An instance of the LLM class or None if failed.
    """
    # Convert provider name to title case for case-insensitive matching
    provider_key = provider.title()
    if provider_key.lower() == 'openai':
        provider_key = 'OpenAI'
    
    if provider_key not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported provider: {provider_key}")

    # Ollama special case — no API key required
    if provider_key == "Ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            if for_agno:
                from agno.models.ollama import Ollama as AgnoOllama
                return AgnoOllama(id=model_name, base_url=base_url)
            else:
                from browser_use import ChatOllama
                return ChatOllama(model=model_name, base_url=base_url)
        except ImportError:
            raise ValueError("Ollama support requires: pip install ollama")
        except Exception as e:
            raise Exception(f"Failed to init Ollama '{model_name}': {e}")

    model_info = SUPPORTED_MODELS[provider_key]["models"].get(model_name)
    if not model_info:
        raise ValueError(f"Unsupported model '{model_name}' for provider '{provider_key}'")

    api_key_env = SUPPORTED_MODELS[provider_key]["api_key_env"]
    api_key = os.environ.get(api_key_env)

    if not api_key:
        raise ValueError(f"Please set the {api_key_env} environment variable.")

    model_class = model_info["agno_class"] if for_agno else model_info["browser_use_class"]
    param_name = model_info["param_name"]
    
    # The browser-use classes consistently use 'model' as the parameter name
    if not for_agno:
        param_name = 'model'

    try:
        # For browser-use classes, we need to pass the model name directly
        if not for_agno:
            return model_class(model=model_name, api_key=api_key)
        else:
            # For agno classes, use the param_name
            return model_class(**{param_name: model_name, "api_key": api_key})

    except Exception as e:
        # A more robust exception handling might be needed depending on each class constructor
        try:
             # Fallback for browser-use classes that might read from env
             if not for_agno:
                 return model_class(model=model_name)
             return model_class(**{param_name: model_name, "api_key": api_key})
        except Exception as e_inner:
            raise Exception(f"Failed to initialize model '{model_name}': {e_inner}")
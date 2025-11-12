"""
Phase-based Model Configuration
Allows configuring different models for different phases via environment variables
"""
import os
from typing import Optional


def get_model_for_phase(phase_number: int, provider_name: Optional[str] = None) -> Optional[str]:
    """
    Get model name for a specific phase from environment variables
    
    Priority:
    1. OLLAMA_PHASE{phase_number}_MODEL (if provider is ollama)
    2. OLLAMA_DEFAULT_MODEL (if provider is ollama and phase-specific not set)
    3. None (use provider default)
    
    Args:
        phase_number: Phase number (1, 2, 3, 4, etc.)
        provider_name: Provider name (e.g., "ollama", "gemini", "openai")
                      If None, checks LLM_PROVIDER env var
    
    Returns:
        Model name to use for this phase, or None to use provider default
        
    Examples:
        >>> # Phase 1 uses dolphin3, Phase 2 uses mixtral
        >>> get_model_for_phase(1, "ollama")  # Returns "dolphin3" if OLLAMA_PHASE1_MODEL=dolphin3
        >>> get_model_for_phase(2, "ollama")  # Returns "mixtral" if OLLAMA_PHASE2_MODEL=mixtral
    """
    # Determine provider name
    if provider_name is None:
        provider_name = os.getenv("LLM_PROVIDER", "").lower()
    else:
        provider_name = provider_name.lower()
    
    # Only apply phase-specific model config for Ollama
    # Other providers (Gemini, OpenAI) don't support per-phase model config via env vars
    if provider_name != "ollama":
        return None
    
    # Check for phase-specific model config
    phase_model_key = f"OLLAMA_PHASE{phase_number}_MODEL"
    phase_model = os.getenv(phase_model_key)
    
    if phase_model:
        return phase_model.strip()
    
    # Fall back to default Ollama model
    default_model = os.getenv("OLLAMA_DEFAULT_MODEL")
    if default_model:
        return default_model.strip()
    
    # No model specified, use provider default
    return None


def get_all_phase_models(provider_name: Optional[str] = None) -> dict:
    """
    Get all configured phase models as a dictionary
    
    Args:
        provider_name: Provider name (e.g., "ollama")
    
    Returns:
        Dictionary mapping phase numbers to model names
        Example: {1: "dolphin3", 2: "mixtral", 3: "dolphin3"}
    """
    phase_models = {}
    
    # Check for phase-specific configs (Phase 1-10)
    for phase_num in range(1, 11):
        model = get_model_for_phase(phase_num, provider_name)
        if model:
            phase_models[phase_num] = model
    
    return phase_models


"""
Google Gemini LLM Provider
Implements BaseLLMProvider for Google Gemini API
"""
import os
import time
import random
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from src.llm.base_provider import BaseLLMProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None, **kwargs):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Gemini API key (if None, loads from GEMINI_API_KEY env var)
            default_model: Default model to use (if None, uses GEMINI_DEFAULT_MODEL env var or "gemini-2.0-flash")
            **kwargs: Additional Gemini-specific config
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        super().__init__(api_key=api_key, **kwargs)
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in .env file or pass as parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Get default model from parameter, env var, or use recommended default
        if default_model is None:
            default_model = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash")
        
        # Store default model
        self.default_model_name = default_model
        
        # Initialize model with fallback chain
        model_priority = [
            default_model,
            "gemini-2.0-flash",  # Recommended: Good quality, 15 RPM, 1M TPM
            "gemini-2.0-flash-lite",  # Fallback: Lower quality but higher rate limits
        ]
        
        for model_name in model_priority:
            try:
                self._model = genai.GenerativeModel(model_name)
                self.default_model_name = model_name
                logger.info(f"✅ Gemini model initialized: {model_name}")
                break
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize {model_name}: {e}")
                continue
        else:
            # Last resort: try any available model
            try:
                available_models = genai.list_models()
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        self._model = genai.GenerativeModel(model.name)
                        self.default_model_name = model.name
                        logger.warning(f"⚠️  Using fallback model: {model.name}")
                        break
            except Exception as e:
                raise RuntimeError(f"Failed to initialize any Gemini model: {e}")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 5,
        initial_retry_delay: float = 2.0,
        **kwargs
    ) -> str:
        """
        Generate text using Gemini API with automatic retry for rate limits
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Max tokens (Gemini uses max_output_tokens)
            max_retries: Maximum number of retries for rate limit errors (default: 5)
            initial_retry_delay: Initial delay in seconds before retry (default: 2.0)
            **kwargs: Additional Gemini parameters
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If API call fails after all retries
        """
        # Use provided model or default
        model_name = model or self.default_model_name
        
        # Create model instance if different from default
        if model_name != self.default_model_name:
            gen_model = genai.GenerativeModel(model_name)
        else:
            gen_model = self._model
        
        # Configure generation parameters
        generation_config = {
            "temperature": temperature,
            **kwargs
        }
        
        # Gemini uses max_output_tokens instead of max_tokens
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Retry logic with exponential backoff for rate limit errors
        last_exception = None
        retry_delay = initial_retry_delay
        
        for attempt in range(max_retries):
            try:
                response = gen_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                # Success - reset retry delay for next call
                if attempt > 0:
                    logger.info(f"Gemini API call succeeded after {attempt} retries")
                return response.text
                
            except google_exceptions.ResourceExhausted as e:
                # 429 Rate limit error - retry with exponential backoff
                last_exception = e
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter to avoid thundering herd
                    jitter = random.uniform(0, 0.3 * retry_delay)  # Add up to 30% jitter
                    wait_time = retry_delay + jitter
                    
                    logger.warning(
                        f"Gemini API rate limit exceeded (429). "
                        f"Retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait_time)
                    retry_delay *= 2.0  # Exponential backoff
                else:
                    logger.error(
                        f"Gemini API rate limit exceeded after {max_retries} attempts. "
                        f"Please wait and try again later."
                    )
                    
            except Exception as e:
                # For other errors, check if it's a rate limit error by string matching
                error_str = str(e).lower()
                if "429" in error_str or "resource exhausted" in error_str or "rate limit" in error_str:
                    # Handle as rate limit error
                    last_exception = e
                    if attempt < max_retries - 1:
                        jitter = random.uniform(0, 0.3 * retry_delay)
                        wait_time = retry_delay + jitter
                        
                        logger.warning(
                            f"Gemini API rate limit detected. "
                            f"Retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries})..."
                        )
                        time.sleep(wait_time)
                        retry_delay *= 2.0
                    else:
                        logger.error(
                            f"Gemini API rate limit error after {max_retries} attempts: {str(e)}"
                        )
                else:
                    # Non-retryable error - raise immediately
                    logger.error(f"Gemini API error (non-retryable): {str(e)}")
                    raise RuntimeError(f"Gemini API error: {str(e)}")
        
        # If we've exhausted all retries, raise the last exception
        if last_exception:
            raise RuntimeError(
                f"Gemini API error after {max_retries} retries: {str(last_exception)}. "
                f"This is likely a rate limit issue. Please wait and try again later."
            )
        
        # Should not reach here, but just in case
        raise RuntimeError("Gemini API call failed for unknown reason")
    
    def get_available_models(self) -> list:
        """Get list of available Gemini models"""
        try:
            models = genai.list_models()
            return [
                m.name for m in models
                if 'generateContent' in m.supported_generation_methods
            ]
        except Exception:
            # Return common models as fallback
            return [
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.0-flash-exp"
            ]
    
    def get_default_model(self) -> str:
        """Get default Gemini model"""
        return self.default_model_name


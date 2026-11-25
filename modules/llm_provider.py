"""Centralized multi-LLM provider with Groq and Gemini support.

Implements automatic provider selection, health checking, failover,
and unified interface for AI narrative generation and Q&A.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Any, Literal
from enum import Enum

from dotenv import load_dotenv

# Import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("Groq SDK not installed. Install with: pip install groq")

# Import Gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google GenAI SDK not installed. Install with: pip install google-genai")

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers."""
    GROQ = "groq"
    GEMINI = "gemini"
    AUTO = "auto"


@dataclass(frozen=True)
class LLMResponse:
    """Unified LLM response structure."""
    text: str
    provider_used: str
    model_used: str
    success: bool
    error_message: str | None = None


@dataclass(frozen=True)
class ProviderStatus:
    """Provider connection status."""
    provider: str
    connected: bool
    model: str | None = None
    error: str | None = None


class LLMProviderManager:
    """Manages multiple LLM providers with automatic failover."""
    
    def __init__(self):
        """Initialize LLM provider manager."""
        self.groq_client = None
        self.gemini_client = None
        self.active_provider: str | None = None
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize available LLM clients based on configuration."""
        # Initialize Groq
        if GROQ_AVAILABLE:
            groq_key = os.getenv("GROQ_API_KEY", "").strip()
            if groq_key and groq_key != "your_groq_api_key_here":
                try:
                    self.groq_client = Groq(api_key=groq_key)
                    logger.info("Groq client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Groq client: {e}")
        
        # Initialize Gemini
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
            if gemini_key and gemini_key != "your_gemini_api_key_here":
                try:
                    self.gemini_client = genai.Client(api_key=gemini_key)
                    logger.info("Gemini client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini client: {e}")
    
    def get_configured_provider(self) -> str:
        """Get the configured AI provider from environment."""
        provider = os.getenv("AI_PROVIDER", "auto").strip().lower()
        return provider if provider in ["groq", "gemini", "auto"] else "auto"
    
    def is_groq_configured(self) -> bool:
        """Check if Groq is configured."""
        return self.groq_client is not None
    
    def is_gemini_configured(self) -> bool:
        """Check if Gemini is configured."""
        return self.gemini_client is not None
    
    def test_groq_connection(self) -> ProviderStatus:
        """Test Groq API connection with actual request."""
        if not self.is_groq_configured():
            return ProviderStatus(
                provider="groq",
                connected=False,
                error="Groq API key not configured"
            )
        
        try:
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
            # Simple test request
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
                temperature=0.1,
            )
            
            if response and response.choices:
                return ProviderStatus(
                    provider="groq",
                    connected=True,
                    model=model,
                )
            else:
                return ProviderStatus(
                    provider="groq",
                    connected=False,
                    error="Empty response from Groq API"
                )
        except Exception as e:
            logger.error(f"Groq connection test failed: {e}")
            return ProviderStatus(
                provider="groq",
                connected=False,
                error=str(e)
            )
    
    def test_gemini_connection(self) -> ProviderStatus:
        """Test Gemini API connection with actual request."""
        if not self.is_gemini_configured():
            return ProviderStatus(
                provider="gemini",
                connected=False,
                error="Gemini API key not configured"
            )
        
        try:
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp").strip()
            # Simple test request
            response = self.gemini_client.models.generate_content(
                model=model,
                contents="test",
                config=types.GenerateContentConfig(
                    max_output_tokens=10,
                    temperature=0.1,
                ),
            )
            
            if response and response.text:
                return ProviderStatus(
                    provider="gemini",
                    connected=True,
                    model=model,
                )
            else:
                return ProviderStatus(
                    provider="gemini",
                    connected=False,
                    error="Empty response from Gemini API"
                )
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return ProviderStatus(
                provider="gemini",
                connected=False,
                error=str(e)
            )
    
    def get_provider_status(self) -> dict[str, ProviderStatus]:
        """Get status of all providers without testing connection."""
        statuses = {}
        
        # Groq status
        if GROQ_AVAILABLE and self.is_groq_configured():
            statuses["groq"] = ProviderStatus(
                provider="groq",
                connected=True,  # Assumed configured
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            )
        else:
            error = "Not configured" if GROQ_AVAILABLE else "SDK not installed"
            statuses["groq"] = ProviderStatus(
                provider="groq",
                connected=False,
                error=error,
            )
        
        # Gemini status
        if GEMINI_AVAILABLE and self.is_gemini_configured():
            statuses["gemini"] = ProviderStatus(
                provider="gemini",
                connected=True,  # Assumed configured
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            )
        else:
            error = "Not configured" if GEMINI_AVAILABLE else "SDK not installed"
            statuses["gemini"] = ProviderStatus(
                provider="gemini",
                connected=False,
                error=error,
            )
        
        return statuses
    
    def select_provider(self) -> str | None:
        """Select provider based on configuration and availability.
        
        Returns provider name or None if no provider available.
        """
        configured_provider = self.get_configured_provider()
        
        if configured_provider == "groq":
            return "groq" if self.is_groq_configured() else None
        elif configured_provider == "gemini":
            return "gemini" if self.is_gemini_configured() else None
        else:  # auto
            # Priority: Groq -> Gemini
            if self.is_groq_configured():
                return "groq"
            elif self.is_gemini_configured():
                return "gemini"
            else:
                return None
    
    def generate_with_groq(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate response using Groq."""
        if not self.is_groq_configured():
            return LLMResponse(
                text="",
                provider_used="groq",
                model_used="N/A",
                success=False,
                error_message="Groq not configured",
            )
        
        try:
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if response and response.choices and response.choices[0].message:
                return LLMResponse(
                    text=response.choices[0].message.content.strip(),
                    provider_used="groq",
                    model_used=model,
                    success=True,
                )
            else:
                return LLMResponse(
                    text="",
                    provider_used="groq",
                    model_used=model,
                    success=False,
                    error_message="Empty response from Groq",
                )
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return LLMResponse(
                text="",
                provider_used="groq",
                model_used=model if 'model' in locals() else "unknown",
                success=False,
                error_message=str(e),
            )
    
    def generate_with_gemini(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate response using Gemini."""
        if not self.is_gemini_configured():
            return LLMResponse(
                text="",
                provider_used="gemini",
                model_used="N/A",
                success=False,
                error_message="Gemini not configured",
            )
        
        try:
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp").strip()
            
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = self.gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            
            if response and response.text:
                return LLMResponse(
                    text=response.text.strip(),
                    provider_used="gemini",
                    model_used=model,
                    success=True,
                )
            else:
                return LLMResponse(
                    text="",
                    provider_used="gemini",
                    model_used=model,
                    success=False,
                    error_message="Empty response from Gemini",
                )
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return LLMResponse(
                text="",
                provider_used="gemini",
                model_used=model if 'model' in locals() else "unknown",
                success=False,
                error_message=str(e),
            )
    
    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        preferred_provider: str | None = None,
    ) -> LLMResponse:
        """Generate response with automatic provider selection and failover.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            preferred_provider: Optional preferred provider ('groq' or 'gemini')
            
        Returns:
            LLMResponse with generated text and metadata
        """
        # Determine provider to use
        if preferred_provider:
            provider = preferred_provider.lower()
        else:
            provider = self.select_provider()
        
        if not provider:
            return LLMResponse(
                text="",
                provider_used="none",
                model_used="N/A",
                success=False,
                error_message="No LLM provider configured",
            )
        
        # Try primary provider
        if provider == "groq":
            response = self.generate_with_groq(
                prompt, system_instruction, temperature, max_tokens
            )
            
            # Failover to Gemini if Groq fails and Gemini is available
            if not response.success and self.is_gemini_configured():
                logger.warning("Groq failed, failing over to Gemini")
                response = self.generate_with_gemini(
                    prompt, system_instruction, temperature, max_tokens
                )
        
        elif provider == "gemini":
            response = self.generate_with_gemini(
                prompt, system_instruction, temperature, max_tokens
            )
            
            # Failover to Groq if Gemini fails and Groq is available
            if not response.success and self.is_groq_configured():
                logger.warning("Gemini failed, failing over to Groq")
                response = self.generate_with_groq(
                    prompt, system_instruction, temperature, max_tokens
                )
        
        return response


# Global instance
_llm_manager: LLMProviderManager | None = None


def get_llm_manager() -> LLMProviderManager:
    """Get or create global LLM provider manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMProviderManager()
    return _llm_manager


def test_provider_connection(provider: str) -> ProviderStatus:
    """Test connection to specific provider.
    
    Args:
        provider: Provider name ('groq' or 'gemini')
        
    Returns:
        ProviderStatus with connection result
    """
    manager = get_llm_manager()
    
    if provider.lower() == "groq":
        return manager.test_groq_connection()
    elif provider.lower() == "gemini":
        return manager.test_gemini_connection()
    else:
        return ProviderStatus(
            provider=provider,
            connected=False,
            error=f"Unknown provider: {provider}",
        )


def get_all_provider_statuses() -> dict[str, ProviderStatus]:
    """Get status of all providers."""
    manager = get_llm_manager()
    return manager.get_provider_status()


def switch_provider(provider: str) -> bool:
    """Switch active AI provider.
    
    Args:
        provider: Provider to switch to ('groq', 'gemini', or 'auto')
        
    Returns:
        True if switch successful
    """
    if provider not in ["groq", "gemini", "auto"]:
        return False
    
    # Update environment variable
    os.environ["AI_PROVIDER"] = provider
    
    # Update .env file if it exists
    try:
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith("AI_PROVIDER="):
                        f.write(f"AI_PROVIDER={provider}\n")
                    else:
                        f.write(line)
        
        logger.info(f"Switched AI provider to: {provider}")
        return True
    except Exception as e:
        logger.error(f"Failed to update .env file: {e}")
        return False

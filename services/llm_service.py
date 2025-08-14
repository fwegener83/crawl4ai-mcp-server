"""
LLM Service implementations for RAG Query feature.

Provides abstract protocol and concrete implementations for OpenAI and Ollama
LLM providers with comprehensive error handling, configuration management,
and provider switching capabilities.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import httpx

# Optional imports for LLM providers
try:
    from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    APIConnectionError = Exception
    RateLimitError = Exception
    APIError = Exception

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None


class LLMError(Exception):
    """Base exception for LLM service errors."""
    
    def __init__(self, message: str, provider: str, **kwargs):
        super().__init__(message)
        self.provider = provider
        for key, value in kwargs.items():
            setattr(self, key, value)


class LLMUnavailableError(LLMError):
    """Exception raised when LLM service is unavailable."""
    pass


class LLMRateLimitError(LLMError):
    """Exception raised when hitting rate limits."""
    
    def __init__(self, message: str, provider: str, retry_after: Optional[int] = None):
        super().__init__(message, provider)
        self.retry_after = retry_after


class LLMInvalidModelError(LLMError):
    """Exception raised when model is invalid or not found."""
    
    def __init__(self, message: str, provider: str, model: Optional[str] = None):
        super().__init__(message, provider)
        self.model = model


class LLMService(ABC):
    """Abstract protocol for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self, 
        query: str, 
        context: str, 
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Generate LLM response from query and context.
        
        Args:
            query: User's natural language query
            context: Retrieved context from vector search
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature for response generation
            
        Returns:
            Dictionary with response data:
            {
                "success": bool,
                "answer": str,
                "provider": str,
                "model": str,
                "token_usage": {"total": int, "prompt": int, "completion": int},
                "response_time_ms": int
            }
            
        Raises:
            LLMUnavailableError: When service is unavailable
            LLMRateLimitError: When hitting rate limits
            LLMInvalidModelError: When model is invalid
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if LLM service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        pass


class OpenAILLMService(LLMService):
    """OpenAI LLM service implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        if not api_key or not api_key.strip():
            raise ValueError("API key is required for OpenAI service")
        if not model or not model.strip():
            raise ValueError("Model is required for OpenAI service")
        
        self.api_key = api_key
        self.model = model
        self.provider = "openai"
        self._client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(
        self, 
        query: str, 
        context: str, 
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        start_time = time.time()
        
        try:
            # Construct messages following best practices
            system_prompt = f"""You are a helpful assistant that answers questions based on provided context. 
Use the following context to answer the user's question. If the context doesn't contain enough information 
to answer the question, say so clearly.

Context:
{context}"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Make API call
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract response data
            answer = response.choices[0].message.content
            token_usage = {
                "total": response.usage.total_tokens,
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens
            }
            
            return {
                "success": True,
                "answer": answer,
                "provider": self.provider,
                "model": self.model,
                "token_usage": token_usage,
                "response_time_ms": response_time_ms
            }
            
        except APIConnectionError as e:
            raise LLMUnavailableError(
                f"OpenAI API connection failed: {str(e)}", 
                provider=self.provider
            )
        
        except RateLimitError as e:
            retry_after = None
            if hasattr(e.response, 'headers') and 'retry-after' in e.response.headers:
                try:
                    retry_after = int(e.response.headers['retry-after'])
                except (ValueError, TypeError):
                    pass
            
            raise LLMRateLimitError(
                f"OpenAI rate limit exceeded: {str(e)}", 
                provider=self.provider,
                retry_after=retry_after
            )
        
        except APIError as e:
            # Check if it's a model-related error
            error_message = str(e)
            if "model" in error_message.lower() and ("not found" in error_message.lower() or 
                                                      "does not exist" in error_message.lower()):
                raise LLMInvalidModelError(
                    f"OpenAI model error: {error_message}",
                    provider=self.provider,
                    model=self.model
                )
            else:
                raise LLMUnavailableError(
                    f"OpenAI API error: {error_message}",
                    provider=self.provider
                )
        
        except Exception as e:
            raise LLMUnavailableError(
                f"Unexpected OpenAI error: {str(e)}",
                provider=self.provider
            )
    
    async def health_check(self) -> bool:
        """Check OpenAI service health."""
        try:
            # Simple test request
            await self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False


class OllamaLLMService(LLMService):
    """Ollama LLM service implementation."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """
        Initialize Ollama service.
        
        Args:
            host: Ollama server host URL
            model: Model name to use
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama package not available. Install with: pip install ollama")
        if not host or not host.strip():
            raise ValueError("Host is required for Ollama service")
        if not model or not model.strip():
            raise ValueError("Model is required for Ollama service")
        
        self.host = host
        self.model = model
        self.provider = "ollama"
        self._client = ollama.AsyncClient(host=host)
    
    async def generate_response(
        self, 
        query: str, 
        context: str, 
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate response using Ollama API."""
        start_time = time.time()
        
        try:
            # Construct prompt
            prompt = f"""Context: {context}

Question: {query}

Please answer the question based on the provided context. If the context doesn't contain enough information to answer the question, please say so clearly."""
            
            # Make API call
            response = await self._client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract response data
            answer = response['response']
            
            # Calculate token usage (Ollama provides eval counts)
            prompt_tokens = response.get('prompt_eval_count', 0)
            completion_tokens = response.get('eval_count', 0)
            total_tokens = prompt_tokens + completion_tokens
            
            token_usage = {
                "total": total_tokens,
                "prompt": prompt_tokens,
                "completion": completion_tokens
            }
            
            return {
                "success": True,
                "answer": answer,
                "provider": self.provider,
                "model": self.model,
                "token_usage": token_usage,
                "response_time_ms": response_time_ms
            }
            
        except httpx.ConnectError as e:
            raise LLMUnavailableError(
                f"Ollama connection failed: {str(e)}", 
                provider=self.provider
            )
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Model not found
                raise LLMInvalidModelError(
                    f"Ollama model not found: {self.model}",
                    provider=self.provider,
                    model=self.model
                )
            else:
                raise LLMUnavailableError(
                    f"Ollama HTTP error {e.response.status_code}: {e.response.text}",
                    provider=self.provider
                )
        
        except Exception as e:
            raise LLMUnavailableError(
                f"Unexpected Ollama error: {str(e)}",
                provider=self.provider
            )
    
    async def health_check(self) -> bool:
        """Check Ollama service health."""
        try:
            # Simple test request
            await self._client.generate(
                model=self.model,
                prompt="Test",
                options={"num_predict": 1}
            )
            return True
        except Exception:
            return False


class LLMServiceFactory:
    """Factory for creating LLM service instances based on configuration."""
    
    @staticmethod
    def create_service() -> LLMService:
        """
        Create LLM service based on environment configuration.
        
        Environment variables:
            RAG_LLM_PROVIDER: "openai" or "ollama" (default: "openai")
            
            For OpenAI:
                RAG_OPENAI_API_KEY: API key (required)
                RAG_OPENAI_MODEL: Model name (default: "gpt-4o-mini")
            
            For Ollama:
                RAG_OLLAMA_HOST: Host URL (default: "http://localhost:11434")
                RAG_OLLAMA_MODEL: Model name (default: "llama3.1:8b")
        
        Returns:
            Configured LLM service instance
            
        Raises:
            ValueError: When configuration is invalid or missing
        """
        provider = os.getenv("RAG_LLM_PROVIDER", "openai").lower()
        
        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not available. Install with: pip install openai")
            api_key = os.getenv("RAG_OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "RAG_OPENAI_API_KEY environment variable is required for OpenAI provider"
                )
            
            model = os.getenv("RAG_OPENAI_MODEL", "gpt-4o-mini")
            return OpenAILLMService(api_key=api_key, model=model)
        
        elif provider == "ollama":
            if not OLLAMA_AVAILABLE:
                raise ImportError("Ollama package not available. Install with: pip install ollama")
            host = os.getenv("RAG_OLLAMA_HOST")
            if not host:
                host = "http://localhost:11434"  # Default fallback
                
            model = os.getenv("RAG_OLLAMA_MODEL", "llama3.1:8b")
            
            return OllamaLLMService(host=host, model=model)
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Supported providers: openai, ollama")
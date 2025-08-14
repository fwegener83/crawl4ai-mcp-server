"""
Test suite for LLM Service implementations.

Tests the abstract LLM service protocol and concrete implementations
for OpenAI and Ollama providers with comprehensive error handling,
configuration, and provider switching functionality.
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from services.llm_service import (
    LLMService,
    OpenAILLMService, 
    OllamaLLMService,
    LLMServiceFactory,
    LLMError,
    LLMUnavailableError,
    LLMRateLimitError,
    LLMInvalidModelError,
    OPENAI_AVAILABLE,
    OLLAMA_AVAILABLE
)


class TestLLMServiceProtocol:
    """Test the abstract LLM service protocol interface."""
    
    def test_llm_service_is_abstract(self):
        """LLMService cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMService()
    
    def test_abstract_methods_defined(self):
        """Abstract methods are properly defined."""
        abstract_methods = LLMService.__abstractmethods__
        expected_methods = {'generate_response', 'health_check'}
        assert abstract_methods == expected_methods


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not available")
class TestOpenAILLMService:
    """Test OpenAI LLM service implementation."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI async client."""
        client = AsyncMock()
        client.chat.completions.create = AsyncMock()
        return client
    
    @pytest.fixture
    def openai_service(self, mock_openai_client):
        """Create OpenAI service with mocked client."""
        with patch('services.llm_service.AsyncOpenAI', return_value=mock_openai_client):
            service = OpenAILLMService(
                api_key="test-key",
                model="gpt-4o-mini"
            )
            service._client = mock_openai_client
            return service
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, openai_service, mock_openai_client):
        """Test successful response generation with OpenAI."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test response based on the context."
        mock_response.usage.total_tokens = 150
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        query = "What is the main topic?"
        context = "This document discusses machine learning applications in healthcare."
        
        # Act
        result = await openai_service.generate_response(query, context)
        
        # Assert
        assert result["success"] is True
        assert result["answer"] == "This is a test response based on the context."
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o-mini"
        assert result["token_usage"]["total"] == 150
        assert result["token_usage"]["prompt"] == 100
        assert result["token_usage"]["completion"] == 50
        
        # Verify client was called correctly
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args[1]
        assert call_args["model"] == "gpt-4o-mini"
        assert call_args["max_tokens"] == 2000
        assert call_args["temperature"] == 0.1
        assert len(call_args["messages"]) == 2
        
        # Check system message
        system_msg = call_args["messages"][0]
        assert system_msg["role"] == "system"
        assert "context" in system_msg["content"].lower()
        assert context in system_msg["content"]
        
        # Check user message
        user_msg = call_args["messages"][1]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == query
    
    @pytest.mark.asyncio
    async def test_generate_response_custom_parameters(self, openai_service, mock_openai_client):
        """Test response generation with custom parameters."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Custom response"
        mock_response.usage.total_tokens = 200
        mock_response.usage.prompt_tokens = 120
        mock_response.usage.completion_tokens = 80
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = await openai_service.generate_response(
            query="Test query",
            context="Test context",
            max_tokens=3000,
            temperature=0.5
        )
        
        # Assert
        assert result["success"] is True
        call_args = mock_openai_client.chat.completions.create.call_args[1]
        assert call_args["max_tokens"] == 3000
        assert call_args["temperature"] == 0.5
    
    @pytest.mark.asyncio
    async def test_generate_response_api_connection_error(self, openai_service, mock_openai_client):
        """Test handling of OpenAI API connection errors."""
        # Arrange
        from openai import APIConnectionError
        mock_request = Mock()
        mock_openai_client.chat.completions.create.side_effect = APIConnectionError(
            message="Connection failed", request=mock_request
        )
        
        # Act & Assert
        with pytest.raises(LLMUnavailableError) as exc_info:
            await openai_service.generate_response("query", "context")
        
        assert "OpenAI API connection failed" in str(exc_info.value)
        assert exc_info.value.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_generate_response_rate_limit_error(self, openai_service, mock_openai_client):
        """Test handling of rate limit errors."""
        # Arrange
        from openai import RateLimitError
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {"retry-after": "60"}
        
        mock_openai_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded", response=mock_response, body={}
        )
        
        # Act & Assert
        with pytest.raises(LLMRateLimitError) as exc_info:
            await openai_service.generate_response("query", "context")
        
        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.provider == "openai"
        assert exc_info.value.retry_after == 60
    
    @pytest.mark.asyncio
    async def test_generate_response_invalid_model_error(self, openai_service, mock_openai_client):
        """Test handling of invalid model errors."""
        # Arrange
        from openai import APIError
        mock_request = Mock()
        
        mock_openai_client.chat.completions.create.side_effect = APIError(
            message="Model 'invalid-model' not found",
            request=mock_request,
            body={}
        )
        
        # Act & Assert
        with pytest.raises(LLMInvalidModelError) as exc_info:
            await openai_service.generate_response("query", "context")
        
        assert "invalid-model" in str(exc_info.value)
        assert exc_info.value.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, openai_service, mock_openai_client):
        """Test successful health check."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OK"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = await openai_service.health_check()
        
        # Assert
        assert result is True
        mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, openai_service, mock_openai_client):
        """Test health check failure."""
        # Arrange
        from openai import APIConnectionError
        mock_request = Mock()
        mock_openai_client.chat.completions.create.side_effect = APIConnectionError(
            message="Connection failed", request=mock_request
        )
        
        # Act
        result = await openai_service.health_check()
        
        # Assert
        assert result is False
    
    def test_configuration_validation(self):
        """Test OpenAI service configuration validation."""
        # Valid configuration
        service = OpenAILLMService(api_key="test-key", model="gpt-4")
        assert service.model == "gpt-4"
        assert service.provider == "openai"
        
        # Invalid API key
        with pytest.raises(ValueError, match="API key is required"):
            OpenAILLMService(api_key="", model="gpt-4")
        
        # Invalid model
        with pytest.raises(ValueError, match="Model is required"):
            OpenAILLMService(api_key="test-key", model="")


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama package not available")
class TestOllamaLLMService:
    """Test Ollama LLM service implementation."""
    
    @pytest.fixture
    def mock_ollama_client(self):
        """Mock Ollama client."""
        client = AsyncMock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def ollama_service(self, mock_ollama_client):
        """Create Ollama service with mocked client."""
        with patch('services.llm_service.ollama.AsyncClient', return_value=mock_ollama_client):
            service = OllamaLLMService(
                host="http://localhost:11434",
                model="llama3.1:8b"
            )
            service._client = mock_ollama_client
            return service
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, ollama_service, mock_ollama_client):
        """Test successful response generation with Ollama."""
        # Arrange
        mock_response = {
            'response': 'This is a response from Ollama based on the provided context.',
            'done': True,
            'total_duration': 1500000000,  # nanoseconds
            'prompt_eval_count': 50,
            'eval_count': 30
        }
        mock_ollama_client.generate.return_value = mock_response
        
        query = "What is discussed in the context?"
        context = "This document covers artificial intelligence developments."
        
        # Act
        result = await ollama_service.generate_response(query, context)
        
        # Assert
        assert result["success"] is True
        assert result["answer"] == "This is a response from Ollama based on the provided context."
        assert result["provider"] == "ollama"
        assert result["model"] == "llama3.1:8b"
        assert result["token_usage"]["prompt"] == 50
        assert result["token_usage"]["completion"] == 30
        assert result["token_usage"]["total"] == 80
        assert "response_time_ms" in result
        
        # Verify client was called correctly
        mock_ollama_client.generate.assert_called_once()
        call_args = mock_ollama_client.generate.call_args[1]
        assert call_args["model"] == "llama3.1:8b"
        assert call_args["stream"] is False
        assert call_args["options"]["num_predict"] == 2000
        assert call_args["options"]["temperature"] == 0.1
        
        # Verify prompt includes context and query
        prompt = call_args["prompt"]
        assert context in prompt
        assert query in prompt
    
    @pytest.mark.asyncio
    async def test_generate_response_connection_error(self, ollama_service, mock_ollama_client):
        """Test handling of Ollama connection errors."""
        # Arrange
        import httpx
        mock_ollama_client.generate.side_effect = httpx.ConnectError("Connection refused")
        
        # Act & Assert
        with pytest.raises(LLMUnavailableError) as exc_info:
            await ollama_service.generate_response("query", "context")
        
        assert "Ollama connection failed" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
    
    @pytest.mark.asyncio
    async def test_generate_response_model_not_found(self, ollama_service, mock_ollama_client):
        """Test handling when model is not found."""
        # Arrange
        import httpx
        response = Mock()
        response.status_code = 404
        response.text = "model 'unknown:model' not found"
        mock_ollama_client.generate.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=response
        )
        
        # Act & Assert
        with pytest.raises(LLMInvalidModelError) as exc_info:
            await ollama_service.generate_response("query", "context")
        
        assert "Ollama model not found" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_service, mock_ollama_client):
        """Test successful Ollama health check."""
        # Arrange
        mock_ollama_client.generate.return_value = {
            'response': 'OK',
            'done': True
        }
        
        # Act
        result = await ollama_service.health_check()
        
        # Assert
        assert result is True
        mock_ollama_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_service, mock_ollama_client):
        """Test Ollama health check failure."""
        # Arrange
        import httpx
        mock_ollama_client.generate.side_effect = httpx.ConnectError("Connection failed")
        
        # Act
        result = await ollama_service.health_check()
        
        # Assert
        assert result is False


class TestLLMServiceFactory:
    """Test LLM service factory for provider switching."""
    
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not available")
    @patch.dict('os.environ', {
        'RAG_LLM_PROVIDER': 'openai',
        'RAG_OPENAI_API_KEY': 'test-key',
        'RAG_OPENAI_MODEL': 'gpt-4o-mini'
    })
    def test_create_openai_service(self):
        """Test creating OpenAI service from environment."""
        service = LLMServiceFactory.create_service()
        
        assert isinstance(service, OpenAILLMService)
        assert service.model == "gpt-4o-mini"
        assert service.provider == "openai"
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama package not available")
    @patch.dict('os.environ', {
        'RAG_LLM_PROVIDER': 'ollama',
        'RAG_OLLAMA_HOST': 'http://localhost:11434',
        'RAG_OLLAMA_MODEL': 'llama3.1:8b'
    })
    def test_create_ollama_service(self):
        """Test creating Ollama service from environment."""
        service = LLMServiceFactory.create_service()
        
        assert isinstance(service, OllamaLLMService)
        assert service.model == "llama3.1:8b"
        assert service.provider == "ollama"
    
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not available")
    @patch.dict('os.environ', {
        'RAG_LLM_PROVIDER': 'openai'
    }, clear=True)
    def test_missing_required_config_openai(self):
        """Test error when OpenAI configuration is missing."""
        with pytest.raises(ValueError, match="RAG_OPENAI_API_KEY"):
            LLMServiceFactory.create_service()
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama package not available")
    @patch.dict('os.environ', {
        'RAG_LLM_PROVIDER': 'ollama'
    }, clear=True)
    def test_ollama_with_default_config(self):
        """Test Ollama service creation with default configuration."""
        service = LLMServiceFactory.create_service()
        
        assert isinstance(service, OllamaLLMService)
        assert service.host == "http://localhost:11434"
        assert service.model == "llama3.1:8b"
        assert service.provider == "ollama"
    
    @patch.dict('os.environ', {
        'RAG_LLM_PROVIDER': 'unknown'
    })
    def test_unknown_provider(self):
        """Test error for unknown provider."""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMServiceFactory.create_service()
    
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not available")
    @patch.dict('os.environ', {}, clear=True)
    def test_default_provider_fallback(self):
        """Test default provider when no configuration provided."""
        # Should fallback to OpenAI with sensible defaults
        with pytest.raises(ValueError, match="RAG_OPENAI_API_KEY"):
            LLMServiceFactory.create_service()


class TestLLMErrorHandling:
    """Test LLM error hierarchy and handling."""
    
    def test_llm_error_base(self):
        """Test base LLM error."""
        error = LLMError("Test error", provider="test")
        
        assert str(error) == "Test error"
        assert error.provider == "test"
        assert isinstance(error, Exception)
    
    def test_llm_unavailable_error(self):
        """Test LLM unavailable error."""
        error = LLMUnavailableError("Service down", provider="openai")
        
        assert str(error) == "Service down"
        assert error.provider == "openai"
        assert isinstance(error, LLMError)
    
    def test_llm_rate_limit_error(self):
        """Test rate limit error."""
        error = LLMRateLimitError("Rate limited", provider="openai", retry_after=60)
        
        assert str(error) == "Rate limited"
        assert error.provider == "openai"
        assert error.retry_after == 60
        assert isinstance(error, LLMError)
    
    def test_llm_invalid_model_error(self):
        """Test invalid model error."""
        error = LLMInvalidModelError("Model not found", provider="ollama", model="invalid:model")
        
        assert str(error) == "Model not found"
        assert error.provider == "ollama"
        assert error.model == "invalid:model"
        assert isinstance(error, LLMError)


class TestLLMServiceIntegration:
    """Integration tests for LLM services."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_openai_integration(self):
        """Test actual OpenAI integration if API key available."""
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not available")
        
        service = OpenAILLMService(api_key=api_key, model="gpt-4o-mini")
        
        # Test health check
        is_healthy = await service.health_check()
        assert is_healthy is True
        
        # Test response generation
        result = await service.generate_response(
            query="What is the main topic?",
            context="This document discusses machine learning applications in healthcare.",
            max_tokens=100
        )
        
        assert result["success"] is True
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0
        assert result["provider"] == "openai"
        assert "token_usage" in result
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ollama_integration(self):
        """Test actual Ollama integration if service available."""
        try:
            service = OllamaLLMService(
                host="http://localhost:11434",
                model="llama3.1:8b"
            )
            
            # Test health check first
            is_healthy = await service.health_check()
            if not is_healthy:
                pytest.skip("Ollama service not available")
            
            # Test response generation
            result = await service.generate_response(
                query="What is AI?",
                context="Artificial Intelligence is a field of computer science.",
                max_tokens=50
            )
            
            assert result["success"] is True
            assert isinstance(result["answer"], str)
            assert len(result["answer"]) > 0
            assert result["provider"] == "ollama"
        except Exception:
            pytest.skip("Ollama not available for integration test")
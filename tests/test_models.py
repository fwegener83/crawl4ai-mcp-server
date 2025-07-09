"""Test Pydantic model validation and serialization."""
import pytest
from pydantic import ValidationError
import json
from typing import Dict, Any

from tools.web_extract import WebExtractParams


class TestWebExtractParams:
    """Test WebExtractParams model validation and serialization."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        params = WebExtractParams(url="https://example.com")
        assert params.url == "https://example.com"
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        params = WebExtractParams(url="http://example.com")
        assert params.url == "http://example.com"
    
    def test_url_with_subdomain(self):
        """Test URL with subdomain."""
        params = WebExtractParams(url="https://api.example.com")
        assert params.url == "https://api.example.com"
    
    def test_url_with_path(self):
        """Test URL with path."""
        params = WebExtractParams(url="https://example.com/api/v1/data")
        assert params.url == "https://example.com/api/v1/data"
    
    def test_url_with_query_parameters(self):
        """Test URL with query parameters."""
        url = "https://example.com/search?q=test&limit=10"
        params = WebExtractParams(url=url)
        assert params.url == url
    
    def test_url_with_fragment(self):
        """Test URL with fragment."""
        url = "https://example.com/page#section"
        params = WebExtractParams(url=url)
        assert params.url == url
    
    def test_url_with_port(self):
        """Test URL with port."""
        url = "https://example.com:8080/api"
        params = WebExtractParams(url=url)
        assert params.url == url
    
    def test_url_with_auth(self):
        """Test URL with authentication."""
        url = "https://user:pass@example.com/secure"
        params = WebExtractParams(url=url)
        assert params.url == url
    
    def test_url_whitespace_stripped(self):
        """Test that whitespace is stripped from URL."""
        params = WebExtractParams(url="  https://example.com  ")
        assert params.url == "https://example.com"
    
    def test_url_leading_whitespace_stripped(self):
        """Test that leading whitespace is stripped."""
        params = WebExtractParams(url="   https://example.com")
        assert params.url == "https://example.com"
    
    def test_url_trailing_whitespace_stripped(self):
        """Test that trailing whitespace is stripped."""
        params = WebExtractParams(url="https://example.com   ")
        assert params.url == "https://example.com"
    
    def test_empty_string_url_raises_validation_error(self):
        """Test that empty string URL raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WebExtractParams(url="")
        
        assert "URL cannot be empty" in str(exc_info.value)
    
    def test_whitespace_only_url_raises_validation_error(self):
        """Test that whitespace-only URL raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WebExtractParams(url="   ")
        
        assert "URL cannot be empty" in str(exc_info.value)
    
    def test_none_url_raises_validation_error(self):
        """Test that None URL raises validation error."""
        with pytest.raises(ValidationError):
            WebExtractParams(url=None)
    
    def test_invalid_url_format_raises_validation_error(self):
        """Test that invalid URL format raises validation error."""
        invalid_urls = [
            "not-a-url",
            "example.com",
            "www.example.com",
            "://example.com",
            "http://",
            "https://",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError) as exc_info:
                WebExtractParams(url=url)
            
            assert "Invalid URL format" in str(exc_info.value)
    
    def test_unsupported_protocol_raises_validation_error(self):
        """Test that unsupported protocol raises validation error."""
        unsupported_protocols = [
            "ftp://example.com",
            "telnet://example.com",
        ]
        
        for url in unsupported_protocols:
            with pytest.raises(ValidationError) as exc_info:
                WebExtractParams(url=url)
            
            assert "URL must use HTTP or HTTPS protocol" in str(exc_info.value)
    
    def test_mailto_protocol_raises_validation_error(self):
        """Test that mailto protocol raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WebExtractParams(url="mailto:user@example.com")
        
        # mailto URLs have no netloc, so they fail the netloc check
        assert "Invalid URL format" in str(exc_info.value)
    
    def test_file_protocol_raises_validation_error(self):
        """Test that file protocol raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WebExtractParams(url="file:///path/to/file")
        
        # file:// URLs have no netloc, so they fail the netloc check
        assert "Invalid URL format" in str(exc_info.value)
    
    def test_model_serialization_to_dict(self):
        """Test model serialization to dictionary."""
        params = WebExtractParams(url="https://example.com")
        serialized = params.model_dump()
        
        assert isinstance(serialized, dict)
        assert serialized == {"url": "https://example.com"}
    
    def test_model_serialization_to_json(self):
        """Test model serialization to JSON."""
        params = WebExtractParams(url="https://example.com")
        json_str = params.model_dump_json()
        
        assert isinstance(json_str, str)
        
        # Parse JSON to verify it's valid
        parsed = json.loads(json_str)
        assert parsed == {"url": "https://example.com"}
    
    def test_model_deserialization_from_dict(self):
        """Test model deserialization from dictionary."""
        data = {"url": "https://example.com"}
        params = WebExtractParams(**data)
        
        assert params.url == "https://example.com"
    
    def test_model_deserialization_from_json(self):
        """Test model deserialization from JSON string."""
        json_str = '{"url": "https://example.com"}'
        params = WebExtractParams.model_validate_json(json_str)
        
        assert params.url == "https://example.com"
    
    def test_model_field_description(self):
        """Test that model field has correct description."""
        schema = WebExtractParams.model_json_schema()
        
        assert "properties" in schema
        assert "url" in schema["properties"]
        assert "description" in schema["properties"]["url"]
        assert schema["properties"]["url"]["description"] == "URL of the webpage to crawl"
    
    def test_model_field_required(self):
        """Test that URL field is required."""
        schema = WebExtractParams.model_json_schema()
        
        assert "required" in schema
        assert "url" in schema["required"]
    
    def test_model_field_type(self):
        """Test that URL field has correct type."""
        schema = WebExtractParams.model_json_schema()
        
        assert schema["properties"]["url"]["type"] == "string"
    
    def test_model_validation_error_details(self):
        """Test validation error details."""
        try:
            WebExtractParams(url="")
        except ValidationError as e:
            errors = e.errors()
            
            assert len(errors) == 1
            assert errors[0]["type"] == "value_error"
            assert errors[0]["loc"] == ("url",)
            assert "URL cannot be empty" in errors[0]["msg"]
    
    def test_model_validation_error_multiple_fields(self):
        """Test validation error with multiple fields (if we add more)."""
        # This test verifies the validation error structure
        try:
            WebExtractParams(url="invalid-url")
        except ValidationError as e:
            errors = e.errors()
            
            assert len(errors) == 1
            assert errors[0]["loc"] == ("url",)
            assert errors[0]["type"] == "value_error"
    
    def test_model_repr(self):
        """Test model string representation."""
        params = WebExtractParams(url="https://example.com")
        repr_str = repr(params)
        
        assert "WebExtractParams" in repr_str
        assert "https://example.com" in repr_str
    
    def test_model_equality(self):
        """Test model equality comparison."""
        params1 = WebExtractParams(url="https://example.com")
        params2 = WebExtractParams(url="https://example.com")
        params3 = WebExtractParams(url="https://different.com")
        
        assert params1 == params2
        assert params1 != params3
    
    def test_model_hash(self):
        """Test model hashing."""
        params1 = WebExtractParams(url="https://example.com")
        params2 = WebExtractParams(url="https://example.com")
        
        # Models should be hashable (because they're frozen)
        assert hash(params1) == hash(params2)
        
        # Can be used in sets
        param_set = {params1, params2}
        assert len(param_set) == 1
    
    def test_model_immutability(self):
        """Test that model is immutable after creation."""
        params = WebExtractParams(url="https://example.com")
        
        # Should not be able to modify the URL after creation (frozen model)
        with pytest.raises(ValidationError):
            params.url = "https://changed.com"
    
    def test_model_copy(self):
        """Test model copying."""
        params = WebExtractParams(url="https://example.com")
        copied = params.model_copy()
        
        assert copied == params
        assert copied is not params
    
    def test_model_copy_with_changes(self):
        """Test model copying with changes."""
        params = WebExtractParams(url="https://example.com")
        copied = params.model_copy(update={"url": "https://changed.com"})
        
        assert copied.url == "https://changed.com"
        assert params.url == "https://example.com"
    
    def test_model_validation_with_extra_fields(self):
        """Test model validation with extra fields."""
        # Should ignore extra fields by default
        data = {
            "url": "https://example.com",
            "extra_field": "ignored"
        }
        
        params = WebExtractParams(**data)
        assert params.url == "https://example.com"
        assert not hasattr(params, "extra_field")
    
    def test_model_schema_generation(self):
        """Test JSON schema generation."""
        schema = WebExtractParams.model_json_schema()
        
        # Check basic schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "title" in schema
        
        # Check URL field schema
        url_schema = schema["properties"]["url"]
        assert url_schema["type"] == "string"
        assert url_schema["description"] == "URL of the webpage to crawl"
    
    def test_model_with_complex_urls(self):
        """Test model with complex real-world URLs."""
        complex_urls = [
            "https://api.github.com/repos/owner/repo/contents/path?ref=main",
            "https://www.google.com/search?q=python+testing&ie=UTF-8",
            "https://example.com/path/to/resource?param1=value1&param2=value2#section",
            "https://user:password@secure.example.com:8443/api/v1/data",
            "https://subdomain.example.co.uk/very/long/path/to/resource",
        ]
        
        for url in complex_urls:
            params = WebExtractParams(url=url)
            assert params.url == url
    
    def test_model_validation_performance(self):
        """Test that model validation is performant."""
        import time
        
        # Create many instances quickly
        start_time = time.time()
        
        for i in range(1000):
            params = WebExtractParams(url=f"https://example{i}.com")
            assert params.url == f"https://example{i}.com"
        
        end_time = time.time()
        
        # Should complete quickly (less than 1 second for 1000 instances)
        assert end_time - start_time < 1.0
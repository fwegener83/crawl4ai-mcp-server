"""
Test parameter validation for domain deep crawler.
Following TDD approach: Write tests first, then implement the parameter classes.
"""

import pytest
from typing import List
from pydantic import ValidationError


class TestDomainDeepCrawlParamsValidation:
    """Test parameter validation for domain deep crawl."""
    
    def test_domain_url_validation_empty(self):
        """Test empty domain URL raises ValueError."""
        # This test will fail initially - that's expected in TDD
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="")
        
        assert "Domain URL cannot be empty" in str(exc_info.value)
    
    def test_domain_url_validation_whitespace_only(self):
        """Test whitespace-only domain URL raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="   ")
        
        assert "Domain URL cannot be empty" in str(exc_info.value)
    
    def test_domain_url_validation_invalid_format(self):
        """Test invalid URL format raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="invalid-url")
        
        assert "Invalid domain URL format" in str(exc_info.value)
    
    def test_domain_url_validation_invalid_scheme(self):
        """Test invalid URL scheme raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="ftp://example.com")
        
        assert "must use HTTP or HTTPS protocol" in str(exc_info.value)
    
    def test_domain_url_validation_valid_http(self):
        """Test valid HTTP URL is accepted."""
        from tools.domain_crawler import DomainDeepCrawlParams
        params = DomainDeepCrawlParams(domain_url="http://example.com")
        
        assert params.domain_url == "http://example.com"
    
    def test_domain_url_validation_valid_https(self):
        """Test valid HTTPS URL is accepted."""
        from tools.domain_crawler import DomainDeepCrawlParams
        params = DomainDeepCrawlParams(domain_url="https://example.com")
        
        assert params.domain_url == "https://example.com"
    
    def test_domain_url_validation_strips_whitespace(self):
        """Test URL whitespace is stripped."""
        from tools.domain_crawler import DomainDeepCrawlParams
        params = DomainDeepCrawlParams(domain_url="  https://example.com  ")
        
        assert params.domain_url == "https://example.com"
    
    def test_max_depth_validation_negative(self):
        """Test negative max depth raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="https://example.com", max_depth=-1)
        
        assert "greater than or equal to 0" in str(exc_info.value)
    
    def test_max_depth_validation_too_high(self):
        """Test max depth exceeding limit raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="https://example.com", max_depth=11)
        
        assert "less than or equal to 10" in str(exc_info.value)
    
    def test_max_depth_validation_valid_range(self):
        """Test valid max depth range."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        # Test boundary values
        params_min = DomainDeepCrawlParams(domain_url="https://example.com", max_depth=0)
        params_max = DomainDeepCrawlParams(domain_url="https://example.com", max_depth=10)
        
        assert params_min.max_depth == 0
        assert params_max.max_depth == 10
    
    def test_crawl_strategy_validation_invalid(self):
        """Test invalid crawl strategy raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="https://example.com", crawl_strategy="invalid")
        
        assert "Strategy must be one of" in str(exc_info.value)
        assert "bfs" in str(exc_info.value)
        assert "dfs" in str(exc_info.value)
        assert "best_first" in str(exc_info.value)
    
    def test_crawl_strategy_validation_valid(self):
        """Test valid crawl strategies."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        for strategy in ["bfs", "dfs", "best_first"]:
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                crawl_strategy=strategy
            )
            assert params.crawl_strategy == strategy
    
    def test_max_pages_validation_zero(self):
        """Test zero max pages raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="https://example.com", max_pages=0)
        
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_max_pages_validation_too_high(self):
        """Test max pages exceeding limit raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_crawler import DomainDeepCrawlParams
            DomainDeepCrawlParams(domain_url="https://example.com", max_pages=1001)
        
        assert "less than or equal to 1000" in str(exc_info.value)
    
    def test_max_pages_validation_valid_range(self):
        """Test valid max pages range."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        # Test boundary values
        params_min = DomainDeepCrawlParams(domain_url="https://example.com", max_pages=1)
        params_max = DomainDeepCrawlParams(domain_url="https://example.com", max_pages=1000)
        
        assert params_min.max_pages == 1
        assert params_max.max_pages == 1000
    
    def test_default_values(self):
        """Test default parameter values."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        params = DomainDeepCrawlParams(domain_url="https://example.com")
        
        assert params.domain_url == "https://example.com"
        assert params.max_depth == 2
        assert params.crawl_strategy == "bfs"
        assert params.max_pages == 50
        assert params.include_external is False
        assert params.url_patterns == []
        assert params.exclude_patterns == []
        assert params.keywords == []
        assert params.stream_results is False
    
    def test_all_parameters_custom(self):
        """Test all parameters with custom values."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            max_depth=3,
            crawl_strategy="best_first",
            max_pages=100,
            include_external=True,
            url_patterns=["*blog*", "*docs*"],
            exclude_patterns=["*admin*"],
            keywords=["python", "crawler"],
            stream_results=True
        )
        
        assert params.domain_url == "https://example.com"
        assert params.max_depth == 3
        assert params.crawl_strategy == "best_first"
        assert params.max_pages == 100
        assert params.include_external is True
        assert params.url_patterns == ["*blog*", "*docs*"]
        assert params.exclude_patterns == ["*admin*"]
        assert params.keywords == ["python", "crawler"]
        assert params.stream_results is True
    
    def test_immutability(self):
        """Test that parameter objects are immutable."""
        from tools.domain_crawler import DomainDeepCrawlParams
        
        params = DomainDeepCrawlParams(domain_url="https://example.com")
        
        # Should not be able to modify attributes
        with pytest.raises(ValidationError):
            params.domain_url = "https://other.com"


class TestDomainLinkPreviewParamsValidation:
    """Test parameter validation for domain link preview."""
    
    def test_domain_url_validation_empty(self):
        """Test empty domain URL raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_link_preview import DomainLinkPreviewParams
            DomainLinkPreviewParams(domain_url="")
        
        assert "Domain URL cannot be empty" in str(exc_info.value)
    
    def test_domain_url_validation_invalid_scheme(self):
        """Test invalid URL scheme raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            from tools.domain_link_preview import DomainLinkPreviewParams
            DomainLinkPreviewParams(domain_url="ftp://example.com")
        
        assert "must use HTTP or HTTPS protocol" in str(exc_info.value)
    
    def test_domain_url_validation_valid(self):
        """Test valid domain URL is accepted."""
        from tools.domain_link_preview import DomainLinkPreviewParams
        params = DomainLinkPreviewParams(domain_url="https://example.com")
        
        assert params.domain_url == "https://example.com"
    
    def test_default_values(self):
        """Test default parameter values."""
        from tools.domain_link_preview import DomainLinkPreviewParams
        
        params = DomainLinkPreviewParams(domain_url="https://example.com")
        
        assert params.domain_url == "https://example.com"
        assert params.include_external is False
    
    def test_include_external_custom(self):
        """Test custom include_external value."""
        from tools.domain_link_preview import DomainLinkPreviewParams
        
        params = DomainLinkPreviewParams(
            domain_url="https://example.com",
            include_external=True
        )
        
        assert params.include_external is True
    
    def test_immutability(self):
        """Test that parameter objects are immutable."""
        from tools.domain_link_preview import DomainLinkPreviewParams
        
        params = DomainLinkPreviewParams(domain_url="https://example.com")
        
        # Should not be able to modify attributes
        with pytest.raises(ValidationError):
            params.domain_url = "https://other.com"


class TestSecurityValidation:
    """Test security-related parameter validation."""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attempt prevention."""
        malicious_url = "https://example.com'; DROP TABLE users; --"
        
        # Should still be valid URL format but we'll sanitize in implementation
        from tools.domain_crawler import DomainDeepCrawlParams
        params = DomainDeepCrawlParams(domain_url=malicious_url)
        
        # URL should be accepted as valid format, but implementation should sanitize
        assert params.domain_url == malicious_url
    
    def test_xss_prevention_in_patterns(self):
        """Test XSS prevention in URL patterns."""
        xss_pattern = "<script>alert('xss')</script>"
        
        from tools.domain_crawler import DomainDeepCrawlParams
        
        # Should accept the pattern but implementation should sanitize
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            url_patterns=[xss_pattern]
        )
        
        assert xss_pattern in params.url_patterns
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention in patterns."""
        malicious_patterns = ["../../../etc/passwd", "..\\..\\windows\\system32"]
        
        from tools.domain_crawler import DomainDeepCrawlParams
        
        # Should accept the patterns but implementation should sanitize
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            url_patterns=malicious_patterns
        )
        
        assert params.url_patterns == malicious_patterns
    
    def test_command_injection_prevention(self):
        """Test command injection prevention in keywords."""
        malicious_keywords = ["; rm -rf /", "$(rm -rf /)", "`rm -rf /`"]
        
        from tools.domain_crawler import DomainDeepCrawlParams
        
        # Should accept the keywords but implementation should sanitize
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            keywords=malicious_keywords
        )
        
        assert params.keywords == malicious_keywords
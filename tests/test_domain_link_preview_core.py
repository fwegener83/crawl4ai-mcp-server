"""
Test domain link preview core implementation.
Following TDD approach: Write tests first, then implement core logic.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from tests.test_domain_crawler_factory import CrawlResultFactory


class TestDomainLinkPreviewCore:
    """Test core domain link preview implementation."""
    
    @pytest.mark.asyncio
    async def test_domain_link_preview_success(self):
        """Test successful domain link preview."""
        # Arrange
        mock_links = [
            {"url": "https://example.com/about", "text": "About", "type": "internal"},
            {"url": "https://example.com/contact", "text": "Contact", "type": "internal"},
            {"url": "https://external.com", "text": "External", "type": "external"}
        ]
        
        mock_result = CrawlResultFactory.create_link_preview_result(mock_links)
        
        with patch('tools.domain_link_preview.extract_links_from_domain') as mock_extract:
            mock_extract.return_value = json.dumps(mock_result)
            
            # Act
            from tools.domain_link_preview import domain_link_preview_impl, DomainLinkPreviewParams
            
            params = DomainLinkPreviewParams(
                domain_url="https://example.com",
                include_external=True
            )
            
            result = await domain_link_preview_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["total_links"] == 3
            assert result_data["internal_links"] == 2
            assert result_data["external_links"] == 1
            assert result_data["domain"] == "example.com"
    
    @pytest.mark.asyncio
    async def test_domain_link_preview_internal_only(self):
        """Test domain link preview with internal links only."""
        # Arrange
        mock_links = [
            {"url": "https://example.com/about", "text": "About", "type": "internal"},
            {"url": "https://example.com/contact", "text": "Contact", "type": "internal"}
        ]
        
        mock_result = CrawlResultFactory.create_link_preview_result(mock_links)
        
        with patch('tools.domain_link_preview.extract_links_from_domain') as mock_extract:
            mock_extract.return_value = json.dumps(mock_result)
            
            # Act
            from tools.domain_link_preview import domain_link_preview_impl, DomainLinkPreviewParams
            
            params = DomainLinkPreviewParams(
                domain_url="https://example.com",
                include_external=False
            )
            
            result = await domain_link_preview_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["total_links"] == 2
            assert result_data["internal_links"] == 2
            assert result_data["external_links"] == 0
    
    @pytest.mark.asyncio
    async def test_domain_link_preview_error_handling(self):
        """Test error handling in domain link preview."""
        # Arrange
        with patch('tools.domain_link_preview.extract_links_from_domain') as mock_extract:
            mock_extract.side_effect = Exception("Network error")
            
            # Act
            from tools.domain_link_preview import domain_link_preview_impl, DomainLinkPreviewParams
            
            params = DomainLinkPreviewParams(domain_url="https://example.com")
            result = await domain_link_preview_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is False
            assert "error" in result_data
            assert result_data["domain"] == "example.com"
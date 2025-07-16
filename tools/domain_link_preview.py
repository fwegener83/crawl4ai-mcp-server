"""
Domain link preview implementation.
This module provides quick domain link analysis without full crawling.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from urllib.parse import urlparse


class DomainLinkPreviewParams(BaseModel):
    """Parameters for domain link preview."""
    
    model_config = ConfigDict(frozen=True)
    
    domain_url: str = Field(..., description="The base URL/domain to analyze")
    include_external: bool = Field(default=False, description="Include external links")
    
    @field_validator('domain_url')
    @classmethod
    def validate_domain_url(cls, v):
        """Validate domain URL format and scheme."""
        if not v or not v.strip():
            raise ValueError("Domain URL cannot be empty")
        
        # Strip whitespace
        v = v.strip()
        
        # Parse URL
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid domain URL format")
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Domain URL must use HTTP or HTTPS protocol")
        
        return v
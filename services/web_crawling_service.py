"""
Web crawling service implementation.

Implements IWebCrawlingService interface with actual crawling logic
extracted from existing MCP tools. This service is protocol-agnostic
and focuses purely on web crawling business logic.
"""
import logging
from typing import Dict, Any, List
from .interfaces import IWebCrawlingService, CrawlResult, DeepCrawlConfig, LinkPreview

# Import existing tools
from tools.web_extract import web_content_extract
from tools.mcp_domain_tools import domain_deep_crawl, domain_link_preview

logger = logging.getLogger(__name__)


class WebCrawlingService(IWebCrawlingService):
    """
    Implementation of web crawling service.
    
    Delegates to existing crawling tools while providing a clean,
    protocol-agnostic interface for business logic.
    """
    
    def __init__(self):
        """Initialize the web crawling service."""
        logger.info("Initializing WebCrawlingService")
    
    async def extract_content(self, url: str, **kwargs) -> CrawlResult:
        """
        Extract content from a single web page.
        
        Args:
            url: URL to extract content from
            **kwargs: Additional extraction parameters
            
        Returns:
            CrawlResult with extracted content and metadata
        """
        try:
            logger.info(f"Extracting content from URL: {url}")
            
            # Use existing web_content_extract tool
            result = await web_content_extract(url)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            # Convert to CrawlResult
            if result.get("success", False):
                return CrawlResult(
                    url=url,
                    content=result.get("content", ""),
                    metadata={
                        "title": result.get("title", ""),
                        "word_count": len(result.get("content", "").split()),
                        "extraction_method": "crawl4ai"
                    }
                )
            else:
                return CrawlResult(
                    url=url,
                    content="",
                    error=result.get("error", "Failed to extract content"),
                    metadata={}
                )
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return CrawlResult(
                url=url,
                content="",
                error=str(e),
                metadata={}
            )
    
    async def deep_crawl(self, config: DeepCrawlConfig) -> List[CrawlResult]:
        """
        Perform deep crawling of a domain.
        
        Args:
            config: Deep crawl configuration
            
        Returns:
            List of CrawlResult objects for all crawled pages
        """
        try:
            logger.info(f"Starting deep crawl of domain: {config.domain_url}")
            
            # Convert config to parameters for existing tool
            crawl_params = {
                "domain_url": config.domain_url,
                "max_depth": config.max_depth,
                "max_pages": config.max_pages,
                "crawl_strategy": config.crawl_strategy,
                "include_external": config.include_external
            }
            
            if config.url_patterns:
                crawl_params["url_patterns"] = config.url_patterns
            if config.exclude_patterns:
                crawl_params["exclude_patterns"] = config.exclude_patterns
            
            # Use existing domain_deep_crawl tool
            result = await domain_deep_crawl(**crawl_params)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            crawl_results = []
            
            if result.get("success", False):
                pages = result.get("pages", [])
                for page_data in pages:
                    crawl_result = CrawlResult(
                        url=page_data.get("url", ""),
                        content=page_data.get("content", ""),
                        metadata={
                            "title": page_data.get("title", ""),
                            "depth": page_data.get("depth", 0),
                            "word_count": len(page_data.get("content", "").split()),
                            "crawl_strategy": config.crawl_strategy
                        }
                    )
                    if page_data.get("error"):
                        crawl_result.error = page_data["error"]
                    
                    crawl_results.append(crawl_result)
            
            logger.info(f"Deep crawl completed. Retrieved {len(crawl_results)} pages")
            return crawl_results
            
        except Exception as e:
            logger.error(f"Error during deep crawl of {config.domain_url}: {str(e)}")
            return [CrawlResult(
                url=config.domain_url,
                content="",
                error=str(e),
                metadata={"crawl_strategy": config.crawl_strategy}
            )]
    
    async def preview_links(self, domain_url: str, include_external: bool = False) -> LinkPreview:
        """
        Preview available links on a domain.
        
        Args:
            domain_url: Domain to preview links for
            include_external: Whether to include external links
            
        Returns:
            LinkPreview with available links
        """
        try:
            logger.info(f"Previewing links for domain: {domain_url}")
            
            # Use existing domain_link_preview tool
            result = await domain_link_preview(
                domain_url=domain_url,
                include_external=include_external
            )
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return LinkPreview(
                    domain=domain_url,
                    links=result.get("links", []),
                    external_links=result.get("external_links", []) if include_external else None,
                    metadata={
                        "total_links": len(result.get("links", [])),
                        "external_count": len(result.get("external_links", [])) if include_external else 0,
                        "preview_timestamp": result.get("timestamp", "")
                    }
                )
            else:
                return LinkPreview(
                    domain=domain_url,
                    links=[],
                    external_links=None,  # Always None on failure regardless of include_external
                    metadata={
                        "error": result.get("error", "Failed to preview links"),
                        "total_links": 0,
                        "external_count": 0
                    }
                )
                
        except Exception as e:
            logger.error(f"Error previewing links for {domain_url}: {str(e)}")
            return LinkPreview(
                domain=domain_url,
                links=[],
                external_links=None,  # Always None on exception
                metadata={
                    "error": str(e),
                    "total_links": 0,
                    "external_count": 0
                }
            )
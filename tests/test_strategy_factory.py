"""
Test strategy factory for domain deep crawler.
Following TDD approach: Write tests first, then implement the strategy factory.
"""

import pytest
from unittest.mock import MagicMock


class TestStrategyFactory:
    """Test strategy factory functionality."""
    
    def test_bfs_strategy_creation(self):
        """Test BFS strategy creation with correct parameters."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        strategy = create_crawl_strategy(
            strategy_name="bfs",
            max_depth=2,
            max_pages=50,
            filter_chain=None,
            keywords=[]
        )
        
        # Check implementation (real or mock)
        assert strategy is not None
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
            assert isinstance(strategy, BFSDeepCrawlStrategy)
        else:
            # Mock implementation check
            assert hasattr(strategy, 'max_depth')
            assert hasattr(strategy, 'max_pages')
        assert strategy.max_depth == 2
        assert strategy.max_pages == 50
    
    def test_dfs_strategy_creation(self):
        """Test DFS strategy creation with correct parameters."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        strategy = create_crawl_strategy(
            strategy_name="dfs",
            max_depth=3,
            max_pages=30,
            filter_chain=None,
            keywords=[]
        )
        
        assert strategy is not None
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import DFSDeepCrawlStrategy
            assert isinstance(strategy, DFSDeepCrawlStrategy)
        else:
            assert hasattr(strategy, 'max_depth')
            assert hasattr(strategy, 'max_pages')
        assert strategy.max_depth == 3
        assert strategy.max_pages == 30
    
    def test_best_first_strategy_creation(self):
        """Test BestFirst strategy creation with correct parameters."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        strategy = create_crawl_strategy(
            strategy_name="best_first",
            max_depth=2,
            max_pages=25,
            filter_chain=None,
            keywords=["python", "crawler"]
        )
        
        assert strategy is not None
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
            assert isinstance(strategy, BestFirstCrawlingStrategy)
            assert strategy.url_scorer is not None  # Should have scorer with keywords
        else:
            assert hasattr(strategy, 'max_depth')
            assert hasattr(strategy, 'max_pages')
        assert strategy.max_depth == 2
        assert strategy.max_pages == 25
    
    def test_best_first_strategy_with_keywords(self):
        """Test BestFirst strategy with keyword scorer."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        keywords = ["python", "crawling", "tutorial"]
        strategy = create_crawl_strategy(
            strategy_name="best_first",
            max_depth=3,
            max_pages=25,
            filter_chain=None,
            keywords=keywords
        )
        
        assert strategy is not None
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
            assert isinstance(strategy, BestFirstCrawlingStrategy)
            assert strategy.url_scorer is not None
            assert strategy.url_scorer._keywords == keywords
        else:
            assert hasattr(strategy, 'max_depth')
            assert hasattr(strategy, 'max_pages')
            if hasattr(strategy, 'url_scorer') and strategy.url_scorer:
                assert strategy.url_scorer._keywords == keywords
    
    def test_best_first_strategy_without_keywords(self):
        """Test BestFirst strategy without keywords."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        strategy = create_crawl_strategy(
            strategy_name="best_first",
            max_depth=2,
            max_pages=25,
            filter_chain=None,
            keywords=[]
        )
        
        assert strategy is not None
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
            assert isinstance(strategy, BestFirstCrawlingStrategy)
            assert strategy.url_scorer is None  # No scorer when no keywords
        else:
            assert hasattr(strategy, 'max_depth')
            assert hasattr(strategy, 'max_pages')
    
    def test_strategy_with_filter_chain(self):
        """Test strategy creation with filter chain."""
        from tools.domain_crawler import create_crawl_strategy
        
        mock_filter_chain = MagicMock()
        mock_filter_chain.filters = ["domain_filter", "pattern_filter"]
        
        strategy = create_crawl_strategy(
            strategy_name="bfs",
            max_depth=2,
            max_pages=50,
            filter_chain=mock_filter_chain,
            keywords=[]
        )
        
        assert strategy is not None
        assert strategy.filter_chain == mock_filter_chain
    
    def test_invalid_strategy_name(self):
        """Test invalid strategy name raises ValueError."""
        from tools.domain_crawler import create_crawl_strategy
        
        with pytest.raises(ValueError) as exc_info:
            create_crawl_strategy(
                strategy_name="invalid_strategy",
                max_depth=2,
                max_pages=50,
                filter_chain=None,
                keywords=[]
            )
        
        assert "Unknown strategy" in str(exc_info.value)
        assert "invalid_strategy" in str(exc_info.value)
    
    def test_strategy_parameter_validation(self):
        """Test strategy parameter validation."""
        from tools.domain_crawler import create_crawl_strategy
        
        # Test with valid parameters
        strategy = create_crawl_strategy(
            strategy_name="bfs",
            max_depth=5,
            max_pages=100,
            filter_chain=None,
            keywords=[]
        )
        
        assert strategy.max_depth == 5
        assert strategy.max_pages == 100
    
    def test_strategy_configuration_inheritance(self):
        """Test that strategy inherits configuration correctly."""
        from tools.domain_crawler import create_crawl_strategy, CRAWL4AI_AVAILABLE
        
        # Test that different strategies get different configurations
        bfs_strategy = create_crawl_strategy("bfs", 2, 50, None, [])
        dfs_strategy = create_crawl_strategy("dfs", 3, 30, None, [])
        
        if CRAWL4AI_AVAILABLE:
            from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, DFSDeepCrawlStrategy
            assert isinstance(bfs_strategy, BFSDeepCrawlStrategy)
            assert isinstance(dfs_strategy, DFSDeepCrawlStrategy)
        else:
            assert hasattr(bfs_strategy, 'max_depth')
            assert hasattr(dfs_strategy, 'max_depth')
        assert bfs_strategy.max_depth == 2
        assert dfs_strategy.max_depth == 3
        assert bfs_strategy.max_pages == 50
        assert dfs_strategy.max_pages == 30


class TestFilterChainBuilder:
    """Test filter chain building functionality."""
    
    def test_build_filter_chain_basic(self):
        """Test basic filter chain building."""
        from tools.domain_crawler import build_filter_chain
        
        filter_chain = build_filter_chain(
            domain_url="https://example.com",
            include_external=False,
            url_patterns=[],
            exclude_patterns=[]
        )
        
        assert filter_chain is not None
        assert len(filter_chain.filters) >= 1  # At least domain filter
    
    def test_build_filter_chain_with_patterns(self):
        """Test filter chain building with URL patterns."""
        from tools.domain_crawler import build_filter_chain
        
        filter_chain = build_filter_chain(
            domain_url="https://example.com",
            include_external=False,
            url_patterns=["*blog*", "*docs*"],
            exclude_patterns=["*admin*"]
        )
        
        assert filter_chain is not None
        assert len(filter_chain.filters) >= 2  # Domain + pattern filters
    
    def test_build_filter_chain_with_external(self):
        """Test filter chain building with external links allowed."""
        from tools.domain_crawler import build_filter_chain
        
        filter_chain = build_filter_chain(
            domain_url="https://example.com",
            include_external=True,
            url_patterns=[],
            exclude_patterns=[]
        )
        
        assert filter_chain is not None
        # Should have fewer filters when external links are allowed (no domain filter)
        assert len(filter_chain.filters) == 0
    
    def test_build_filter_chain_domain_extraction(self):
        """Test that domain is correctly extracted from URL."""
        from tools.domain_crawler import build_filter_chain
        
        filter_chain = build_filter_chain(
            domain_url="https://subdomain.example.com/path?param=value",
            include_external=False,
            url_patterns=[],
            exclude_patterns=[]
        )
        
        assert filter_chain is not None
        # Should have domain filter for internal links only
        assert len(filter_chain.filters) >= 1
    
    def test_build_filter_chain_pattern_validation(self):
        """Test that patterns are validated."""
        from tools.domain_crawler import build_filter_chain
        
        # Should accept valid patterns
        filter_chain = build_filter_chain(
            domain_url="https://example.com",
            include_external=False,
            url_patterns=["*/blog/*", "*/docs/*"],
            exclude_patterns=["*/admin/*"]
        )
        
        assert filter_chain is not None
        # Should have domain filter + pattern filters
        assert len(filter_chain.filters) >= 2


class TestKeywordScorer:
    """Test keyword scorer functionality."""
    
    def test_keyword_scorer_creation(self):
        """Test keyword scorer creation."""
        from tools.domain_crawler import create_keyword_scorer, CRAWL4AI_AVAILABLE
        
        scorer = create_keyword_scorer(
            keywords=["python", "crawler", "tutorial"],
            weight=0.8
        )
        
        assert scorer is not None
        assert scorer._keywords == ["python", "crawler", "tutorial"]
        if CRAWL4AI_AVAILABLE:
            assert abs(scorer.weight - 0.8) < 0.01
        else:
            assert scorer.weight == 0.8
    
    def test_keyword_scorer_empty_keywords(self):
        """Test keyword scorer with empty keywords."""
        from tools.domain_crawler import create_keyword_scorer
        
        scorer = create_keyword_scorer(keywords=[], weight=0.5)
        
        # Should return None or empty scorer when no keywords
        assert scorer is None or scorer._keywords == []
    
    def test_keyword_scorer_weight_validation(self):
        """Test keyword scorer weight validation."""
        from tools.domain_crawler import create_keyword_scorer, CRAWL4AI_AVAILABLE
        
        # Test valid weights
        scorer = create_keyword_scorer(keywords=["test"], weight=0.5)
        if CRAWL4AI_AVAILABLE:
            assert abs(scorer.weight - 0.5) < 0.01
        else:
            assert scorer.weight == 0.5
        
        scorer = create_keyword_scorer(keywords=["test"], weight=1.0)
        if CRAWL4AI_AVAILABLE:
            assert abs(scorer.weight - 1.0) < 0.01
        else:
            assert scorer.weight == 1.0
        
        scorer = create_keyword_scorer(keywords=["test"], weight=0.0)
        if CRAWL4AI_AVAILABLE:
            assert abs(scorer.weight - 0.0) < 0.01
        else:
            assert scorer.weight == 0.0
    
    def test_keyword_scorer_normalization(self):
        """Test keyword scorer normalizes keywords."""
        from tools.domain_crawler import create_keyword_scorer, CRAWL4AI_AVAILABLE
        
        scorer = create_keyword_scorer(
            keywords=["Python", "CRAWLER", "Tutorial"],
            weight=0.7
        )
        
        # Keywords are normalized to lowercase by the scorer
        assert scorer._keywords == ["python", "crawler", "tutorial"]
        if CRAWL4AI_AVAILABLE:
            assert abs(scorer.weight - 0.7) < 0.01
        else:
            assert scorer.weight == 0.7
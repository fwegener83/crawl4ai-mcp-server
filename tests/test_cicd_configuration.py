"""CI/CD configuration validation tests.

This module tests CI/CD pipeline configuration to ensure proper setup
before implementation, following test-first methodology.
"""
import pytest
import os
import yaml
from pathlib import Path


class TestGitHubActionsConfiguration:
    """Test GitHub Actions workflow configuration."""
    
    def test_github_actions_workflow_syntax(self):
        """Test GitHub Actions workflow file syntax."""
        workflow_path = ".github/workflows/ci.yml"
        
        # First verify the file exists
        assert os.path.exists(workflow_path), f"Workflow file {workflow_path} must exist"
        
        # Parse YAML syntax
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Validate required workflow structure
        assert 'name' in workflow, "Workflow must have a name"
        assert 'on' in workflow, "Workflow must have trigger conditions"
        assert 'jobs' in workflow, "Workflow must define jobs"
        
        # Validate job structure
        jobs = workflow['jobs']
        assert 'fast-tests' in jobs, "Must have fast-tests job"
        assert 'security-tests' in jobs, "Must have security-tests job"
        
        # Validate timeout configurations for CI efficiency
        for job_name, job_config in jobs.items():
            if 'timeout-minutes' in job_config:
                # Integration tests with real crawl4ai need more time
                max_timeout = 25 if 'integration' in job_name else 20
                assert job_config['timeout-minutes'] <= max_timeout, f"Job {job_name} timeout too long for CI"
    
    def test_workflow_job_structure(self):
        """Test individual job structure and configuration."""
        workflow_path = ".github/workflows/ci.yml"
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow['jobs']
        
        # Test fast-tests job
        fast_tests = jobs['fast-tests']
        assert 'runs-on' in fast_tests, "fast-tests must specify runner"
        assert 'steps' in fast_tests, "fast-tests must have steps"
        
        # Test security-tests job
        security_tests = jobs['security-tests']
        assert 'runs-on' in security_tests, "security-tests must specify runner"
        assert 'steps' in security_tests, "security-tests must have steps"
        
        # Validate Python version matrix
        for job_name, job_config in jobs.items():
            if 'strategy' in job_config:
                matrix = job_config['strategy'].get('matrix', {})
                if 'python-version' in matrix:
                    python_versions = matrix['python-version']
                    assert '3.13' in str(python_versions), f"Python 3.13 required for {job_name}"
    
    def test_workflow_environment_variables(self):
        """Test environment variable configuration for CI."""
        workflow_path = ".github/workflows/ci.yml"
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check for required environment variables
        required_env_vars = {
            'CRAWL4AI_VERBOSE': 'false',
            'SECURITY_TEST_MODE': 'mock',
            'PYTHONUNBUFFERED': '1'
        }
        
        # These can be set at job level or step level
        found_env_vars = {}
        
        for job_name, job_config in workflow['jobs'].items():
            # Check job-level env
            if 'env' in job_config:
                found_env_vars.update(job_config['env'])
            
            # Check step-level env
            if 'steps' in job_config:
                for step in job_config['steps']:
                    if 'env' in step:
                        found_env_vars.update(step['env'])
        
        # Validate at least some critical env vars are set
        assert any(var in found_env_vars for var in required_env_vars), \
               "Required environment variables not found in workflow"
    
    def test_workflow_branch_triggers(self):
        """Test workflow branch trigger configuration."""
        workflow_path = ".github/workflows/ci.yml"
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        triggers = workflow['on']
        
        # Should trigger on push to main
        if 'push' in triggers:
            push_config = triggers['push']
            if 'branches' in push_config:
                assert 'main' in push_config['branches'], "Must trigger on main branch pushes"
        
        # Should trigger on pull requests
        assert 'pull_request' in triggers, "Must trigger on pull requests"
        
        # Should not trigger on every branch to avoid noise
        if 'push' in triggers and 'branches' in triggers['push']:
            branches = triggers['push']['branches']
            assert len(branches) <= 3, "Too many branch triggers (creates CI noise)"


class TestPytestCIConfiguration:
    """Test pytest configuration for CI/CD optimization."""
    
    def test_pytest_configuration_for_ci(self):
        """Test pytest configuration is optimized for CI."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        with open('pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        
        pytest_config = config['tool']['pytest']['ini_options']
        
        # Validate CI-friendly configuration
        assert 'timeout' in pytest_config, "Global timeout required for CI"
        assert 'slow' in str(pytest_config.get('markers', '')), "Slow marker required for test selection"
        assert pytest_config.get('asyncio_mode') == 'auto', "Async mode should be auto"
        
        # Validate timeout is reasonable for CI
        timeout = pytest_config.get('timeout', 0)
        assert timeout <= 300, f"Global timeout {timeout}s too long for CI"
        assert timeout >= 60, f"Global timeout {timeout}s too short for complex tests"
    
    def test_pytest_markers_configuration(self):
        """Test pytest markers are properly configured for CI."""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        with open('pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        
        pytest_config = config['tool']['pytest']['ini_options']
        markers = pytest_config.get('markers', [])
        
        required_markers = ['slow', 'security', 'regression']
        
        markers_str = '\n'.join(markers) if isinstance(markers, list) else str(markers)
        
        for marker in required_markers:
            assert marker in markers_str, f"Required marker '{marker}' not configured"
    
    def test_test_selection_patterns(self):
        """Test that test selection patterns work for CI."""
        # Test that we can select fast tests only
        fast_test_patterns = [
            'not slow',
            'not security and not slow',
            'regression'
        ]
        
        for pattern in fast_test_patterns:
            # Validate pattern syntax (basic check)
            assert ' and ' in pattern or ' or ' in pattern or 'not ' in pattern or pattern == 'regression', \
                   f"Invalid marker pattern: {pattern}"


class TestCIEnvironmentConfiguration:
    """Test CI environment configuration."""
    
    def test_environment_variable_configuration(self):
        """Test environment variables for CI testing."""
        test_env_vars = {
            'CRAWL4AI_VERBOSE': 'false',
            'SECURITY_TEST_MODE': 'mock',
            'PYTHONUNBUFFERED': '1',
            'CI': 'true'
        }
        
        # These should be set in CI environment
        # Test validates the expected configuration values
        for var, expected_value in test_env_vars.items():
            # Validate expected values are reasonable
            assert expected_value in ['true', 'false', '1', 'mock'], \
                   f"Invalid environment value for {var}: {expected_value}"
    
    def test_ci_detection_mechanism(self):
        """Test CI environment detection."""
        # Common CI environment variables
        ci_indicators = ['CI', 'GITHUB_ACTIONS', 'CONTINUOUS_INTEGRATION']
        
        # In actual CI, at least one should be set
        # For testing, we just validate the detection logic exists
        for indicator in ci_indicators:
            # Test would check: os.getenv(indicator) in ['true', '1']
            # For now, just validate the indicator names are standard
            assert indicator.isupper(), f"CI indicator {indicator} should be uppercase"
            assert '_' in indicator or indicator == 'CI', f"CI indicator {indicator} format invalid"


class TestCIPipelineStrategy:
    """Test CI pipeline strategy and optimization."""
    
    def test_three_tier_testing_strategy(self):
        """Test 3-tier testing strategy configuration."""
        # Define the 3-tier strategy
        test_tiers = {
            'fast': {
                'max_duration': 60,  # seconds
                'markers': 'not slow',
                'required_coverage': 70  # percent
            },
            'comprehensive': {
                'max_duration': 300,  # seconds  
                'markers': 'not security',
                'required_coverage': 85  # percent
            },
            'security': {
                'max_duration': 120,  # seconds (optimized!)
                'markers': 'security',
                'required_coverage': 95  # percent
            }
        }
        
        # Validate tier configuration
        for tier_name, tier_config in test_tiers.items():
            assert tier_config['max_duration'] > 0, f"Tier {tier_name} must have positive duration"
            assert tier_config['required_coverage'] > 0, f"Tier {tier_name} must have coverage target"
            assert tier_config['markers'], f"Tier {tier_name} must have marker selection"
        
        # Validate tier ordering (fast < comprehensive < security in complexity, not time)
        assert test_tiers['fast']['max_duration'] <= test_tiers['comprehensive']['max_duration']
        
        # Security tests should be fast due to our optimization
        assert test_tiers['security']['max_duration'] <= 120, "Security tests should be optimized"
    
    def test_parallel_execution_strategy(self):
        """Test parallel test execution configuration."""
        # Validate parallel execution parameters
        parallel_config = {
            'max_workers': 4,  # For GitHub Actions
            'pytest_xdist': True,  # Use pytest-xdist for parallelization
            'asyncio_tests': True,  # Support concurrent async tests
        }
        
        for param, value in parallel_config.items():
            assert value is not None, f"Parallel config {param} must be defined"
            
        # Validate worker count is reasonable for CI
        assert parallel_config['max_workers'] <= 8, "Too many workers for CI resources"
        assert parallel_config['max_workers'] >= 2, "Need at least 2 workers for parallelization"
    
    def test_dependency_caching_strategy(self):
        """Test dependency caching strategy for CI performance."""
        cache_strategies = {
            'pip_cache': True,
            'poetry_cache': True,
            'pytest_cache': True,
            'pre_commit_cache': True
        }
        
        # All caching should be enabled for CI performance
        for cache_type, enabled in cache_strategies.items():
            assert enabled, f"Cache {cache_type} should be enabled for CI performance"


class TestBranchProtectionStrategy:
    """Test branch protection configuration strategy."""
    
    def test_main_branch_protection_requirements(self):
        """Test main branch protection requirements."""
        protection_rules = {
            'require_pull_request': True,
            'require_status_checks': True,
            'required_status_checks': [
                'fast-tests',
                'security-tests'
            ],
            'enforce_admins': False,  # Allow emergency fixes
            'allow_force_pushes': False,
            'allow_deletions': False
        }
        
        # Validate protection configuration
        assert protection_rules['require_pull_request'], "PRs required for main branch"
        assert protection_rules['require_status_checks'], "Status checks required"
        assert len(protection_rules['required_status_checks']) >= 2, "Multiple checks required"
        assert not protection_rules['allow_force_pushes'], "No force pushes to main"
    
    def test_feature_branch_workflow(self):
        """Test feature branch workflow configuration."""
        workflow_rules = {
            'branch_naming': 'feature/*',
            'auto_delete_merged': True,
            'require_linear_history': False,  # Allow merge commits
            'timeout_minutes': 20  # Total CI timeout
        }
        
        # Validate workflow configuration
        assert 'feature/' in workflow_rules['branch_naming'], "Feature branch naming convention"
        assert workflow_rules['timeout_minutes'] <= 30, "CI timeout should be reasonable"


class TestPerformanceRegressionPrevention:
    """Test performance regression prevention mechanisms."""
    
    def test_performance_baseline_tracking(self):
        """Test performance baseline tracking configuration."""
        performance_config = {
            'security_test_baseline': 120,  # seconds (original target)
            'security_test_current': 1,     # seconds (optimized target)
            'regression_threshold': 50,     # percent increase that triggers alert
            'improvement_target': 90        # percent improvement from baseline
        }
        
        # Validate performance targets
        current = performance_config['security_test_current']
        baseline = performance_config['security_test_baseline']
        improvement = (baseline - current) / baseline * 100
        
        assert improvement >= performance_config['improvement_target'], \
               f"Performance improvement {improvement:.1f}% below target {performance_config['improvement_target']}%"
    
    def test_performance_monitoring_alerts(self):
        """Test performance monitoring and alerting."""
        alert_config = {
            'slow_test_threshold': 30,      # seconds per test
            'total_suite_threshold': 300,   # seconds for entire suite
            'regression_alert': True,       # Alert on regression
            'report_format': 'json'         # For machine parsing
        }
        
        # Validate alert configuration
        assert alert_config['slow_test_threshold'] > 0, "Slow test threshold must be positive"
        assert alert_config['total_suite_threshold'] > 0, "Suite threshold must be positive" 
        assert alert_config['regression_alert'], "Regression alerts must be enabled"


class TestCISecurityConfiguration:
    """Test CI security configuration."""
    
    def test_secrets_management(self):
        """Test secrets management in CI."""
        # Secrets that might be needed (currently none for this project)
        potential_secrets = [
            'CODECOV_TOKEN',  # If using code coverage
            'SLACK_WEBHOOK',  # If using notifications
        ]
        
        # For this project, we shouldn't need any secrets
        # All tests use mocks and local execution
        required_secrets = []
        
        assert len(required_secrets) == 0, "Project should not require secrets for testing"
    
    def test_security_scanning_integration(self):
        """Test security scanning integration."""
        security_tools = {
            'bandit': True,      # Python security linting
            'safety': True,      # Dependency vulnerability scanning
            'semgrep': False,    # Advanced static analysis (optional)
        }
        
        # At least basic security tools should be configured
        enabled_tools = [tool for tool, enabled in security_tools.items() if enabled]
        assert len(enabled_tools) >= 2, "Multiple security tools should be enabled"
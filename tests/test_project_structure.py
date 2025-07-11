"""Test project structure validation."""
import os
import pytest
import tomli
from pathlib import Path


def test_project_root_exists():
    """Test that project root directory exists."""
    project_root = Path(".")
    assert project_root.exists()
    assert project_root.is_dir()


def test_required_directories_exist():
    """Test that required directories exist."""
    required_dirs = ["tests", "tools", "examples", ".planning"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        assert dir_path.exists(), f"Directory {dir_name} should exist"
        assert dir_path.is_dir(), f"{dir_name} should be a directory"


def test_pyproject_toml_exists():
    """Test that pyproject.toml exists and is valid."""
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml should exist"
    
    # Test that it's valid TOML
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)
    
    assert "project" in config, "pyproject.toml should have [project] section"
    assert "name" in config["project"], "Project should have a name"
    assert "dependencies" in config["project"], "Project should have dependencies"


def test_required_dependencies_in_pyproject():
    """Test that required dependencies are configured."""
    pyproject_path = Path("pyproject.toml")
    
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)
    
    dependencies = config["project"]["dependencies"]
    
    # Check for required dependencies
    required_deps = ["fastmcp", "crawl4ai", "python-dotenv", "pydantic"]
    
    for dep in required_deps:
        assert any(dep in str(dependency) for dependency in dependencies), \
            f"Required dependency {dep} not found in pyproject.toml"


def test_test_dependencies_configured():
    """Test that test dependencies are configured."""
    pyproject_path = Path("pyproject.toml")
    
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)
    
    # Check for test dependencies
    if "optional-dependencies" in config["project"]:
        test_deps = config["project"]["optional-dependencies"].get("test", [])
        required_test_deps = ["pytest", "pytest-asyncio"]
        
        for dep in required_test_deps:
            assert any(dep in str(dependency) for dependency in test_deps), \
                f"Required test dependency {dep} not found"


def test_env_example_exists():
    """Test that .env.example exists."""
    env_example = Path(".env.example")
    assert env_example.exists(), ".env.example should exist"


def test_git_directory_exists():
    """Test that this is a git repository."""
    git_dir = Path(".git")
    assert git_dir.exists(), "Project should be a git repository"
    assert git_dir.is_dir(), ".git should be a directory"


@pytest.mark.asyncio
async def test_async_testing_works():
    """Test that async testing framework works."""
    # This is a simple test to ensure pytest-asyncio is working
    import asyncio
    
    async def async_function():
        await asyncio.sleep(0.001)
        return "async_works"
    
    result = await async_function()
    assert result == "async_works"
"""Unit tests verifying the SecuritySandbox and safe developer tools."""

import pytest

from app.exceptions import SecurityBreachError
from app.services.tools import (
    SecuritySandbox,
    get_git_status,
    get_system_telemetry,
    read_code_file,
)


def test_sandbox_allows_valid_project_file() -> None:
    """Verify that files within the project boundary pass validation."""
    safe_path = SecuritySandbox.validate_path("pyproject.toml")
    assert safe_path.is_file()
    assert safe_path.name == "pyproject.toml"


def test_sandbox_blocks_directory_traversal() -> None:
    """Verify that path traversal attempts (e.g., ../../etc/passwd) raise SecurityBreachError."""
    with pytest.raises(SecurityBreachError) as exc_info:
        SecuritySandbox.validate_path("../../etc/passwd")

    assert "escapes project boundary" in str(exc_info.value)


def test_sandbox_blocks_sensitive_env_file() -> None:
    """Verify that access to .env is strictly blocked even inside project root."""
    with pytest.raises(SecurityBreachError) as exc_info:
        SecuritySandbox.validate_path(".env")

    assert "protected security file" in str(exc_info.value)


def test_system_telemetry_returns_valid_metrics() -> None:
    """Verify that system telemetry returns expected non-zero percentage ranges."""
    telemetry = get_system_telemetry()

    assert "cpu_percent" in telemetry
    assert "memory_percent" in telemetry
    assert 0.0 <= telemetry["memory_percent"] <= 100.0


def test_git_status_returns_branch() -> None:
    """Verify that git_status detects current git repository branch."""
    status = get_git_status()
    assert "branch" in status
    assert status["branch"] != ""


def test_read_code_file_reads_valid_file() -> None:
    """Verify safe file reading for existing permitted files."""
    content = read_code_file("pyproject.toml")
    assert "[tool.ruff]" in content

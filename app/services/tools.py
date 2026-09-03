"""Sandboxed developer tools for Ultron Copilot.

Enforces strict path containment, secret file blacklisting, and structured logging.
"""

import subprocess
from pathlib import Path

import psutil

from app.config import get_settings
from app.exceptions import SecurityBreachError
from app.logger import get_logger

logger = get_logger("tools")

# Sensitive files and extensions strictly forbidden from tool inspection
BLACKLISTED_PATTERNS = {
    ".env",
    "id_rsa",
    "id_ed25519",
    ".pem",
    ".key",
    ".git",
    "credentials",
    "passwd",
    "shadow",
}


class SecuritySandbox:
    """Guarantees that all file operations remain within the project boundary."""

    @classmethod
    def validate_path(cls, target_path: str | Path) -> Path:
        """Resolve and validate that a path is strictly inside the project root.

        Args:
            target_path: Path string or Path object requested by a tool.

        Returns:
            Resolved absolute Path if authorized.

        Raises:
            SecurityBreachError: If path attempts directory traversal or touches blacklisted files.
        """
        settings = get_settings()
        root = settings.project_root.resolve()

        # Resolve relative to root if relative
        resolved = (
            (root / target_path).resolve()
            if not Path(target_path).is_absolute()
            else Path(target_path).resolve()
        )

        # 1. Path containment check: Must be inside project root
        if not resolved.is_relative_to(root):
            logger.warning(
                "security_sandbox_breach_attempt",
                attempted_path=str(target_path),
                resolved_path=str(resolved),
                project_root=str(root),
            )
            raise SecurityBreachError(
                f"Access denied: '{target_path}' escapes project boundary."
            )

        # 2. Blacklist check
        name_lower = resolved.name.lower()
        for blacklisted in BLACKLISTED_PATTERNS:
            if blacklisted in name_lower or resolved.suffix.lower() == blacklisted:
                logger.warning(
                    "security_sandbox_blacklist_attempt",
                    attempted_file=resolved.name,
                )
                raise SecurityBreachError(
                    f"Access denied: '{resolved.name}' is a protected security file."
                )

        return resolved


def get_system_telemetry() -> dict[str, float]:
    """Retrieve host CPU and memory metrics safely without exposing private data.

    Returns:
        Dictionary containing cpu_percent and memory_percent.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory_percent = psutil.virtual_memory().percent

    logger.info("telemetry_polled", cpu=cpu_percent, memory=memory_percent)
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
    }


def get_git_status() -> dict[str, str]:
    """Retrieve current Git branch and working tree status.

    Returns:
        Dictionary containing branch name and short status summary.
    """
    settings = get_settings()
    root = settings.project_root

    try:
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = branch_proc.stdout.strip()

        status_proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        status = status_proc.stdout.strip() or "clean"

        logger.info("git_status_inspected", branch=branch)
        return {"branch": branch, "status": status}

    except subprocess.SubprocessError as err:
        logger.warning("git_status_failed", error=str(err))
        return {"branch": "unknown", "status": "git unavailable"}


def read_code_file(relative_path: str) -> str:
    """Safely read a file within the project boundary for code review.

    Args:
        relative_path: Path relative to project root.

    Returns:
        The content of the file.

    Raises:
        SecurityBreachError: If path violates security sandbox.
        FileNotFoundError: If the file does not exist.
    """
    safe_path = SecuritySandbox.validate_path(relative_path)

    if not safe_path.is_file():
        raise FileNotFoundError(f"File not found: {relative_path}")

    return safe_path.read_text(encoding="utf-8")

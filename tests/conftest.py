"""
Pytest configuration and fixtures.

This file is automatically loaded by pytest.
Add shared fixtures here.
"""

import pytest


@pytest.fixture
def sample_fixture() -> dict[str, str]:
    """Example fixture - replace with actual fixtures."""
    return {"key": "value"}

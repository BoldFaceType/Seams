"""
Basic smoke tests to verify package installation.
"""

import seams


def test_import() -> None:
    """Verify package can be imported."""
    assert seams.__version__ == "0.1.0"


def test_author() -> None:
    """Verify author is set."""
    assert seams.__author__ == "Jeremie"

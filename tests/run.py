# -*- coding: utf-8 -*-
"""
Test runner for Cp9
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all tests"""
    exit_code = pytest.main([
        str(project_root / "tests"),
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ])
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())

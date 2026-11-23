"""
Pytest configuration and global fixtures.
"""

import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from tests.fixtures.generate_fixtures import create_all_fixtures


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory):
    """Generate all test fixtures in a dedicated directory for the test session."""
    base_dir = tmp_path_factory.mktemp("doc_converter_fixtures")
    fixtures_path = str(base_dir)
    create_all_fixtures(fixtures_path)
    return fixtures_path

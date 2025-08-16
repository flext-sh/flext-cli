"""Test package marker for flext-cli tests.

Ensures that relative imports like `from tests.test_mocks import ...` work
consistently under pytest by treating `tests` as a package.
"""

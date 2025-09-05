"""Test file to debug MyPy BaseModel issue."""

from pydantic import BaseModel


class TestModel(BaseModel):
    """Simple test model."""

    name: str = "test"

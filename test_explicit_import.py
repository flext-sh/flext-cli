"""Test explicit typing approach."""

import pydantic


class TestModel(pydantic.BaseModel):
    """Test model with explicit module reference."""

    name: str = "test"

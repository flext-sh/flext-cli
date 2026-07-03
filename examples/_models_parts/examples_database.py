"""Split example model database namespace."""

from __future__ import annotations

from ipaddress import ip_address
from typing import ClassVar

from examples import c
from flext_cli import m, u


class ExamplesFlextCliModelsExamplesDatabase:
    """Split example model database namespace."""

    class AdvancedDatabaseConfig(m.Value):
        """Database configuration with advanced validation."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        host: str = m.Field(
            description="Database host",
        )
        port: int = m.Field(
            c.EXAMPLE_DEFAULT_DB_PORT,
            description="Database port",
            ge=c.EXAMPLE_MIN_PORT,
            le=c.EXAMPLE_MAX_PORT,
            validate_default=True,
        )
        name: str = m.Field(description="Database name", min_length=1)
        username: str = m.Field(description="Database username", min_length=1)
        password: str = m.Field(
            description="Database password",
            min_length=c.EXAMPLE_MIN_PASSWORD_LENGTH,
        )
        ssl_enabled: bool = m.Field(
            True, description="Enable SSL", validate_default=True
        )
        connection_pool: int = m.Field(
            c.EXAMPLE_DEFAULT_CONNECTION_POOL,
            description="Connection pool size",
            ge=1,
            le=c.EXAMPLE_MAX_CONNECTION_POOL,
            validate_default=True,
        )

        @u.field_validator("host")
        @classmethod
        def validate_host(cls, v: str) -> str:
            """Ensure host looks like a hostname or IP."""
            host = v.strip()
            if not host:
                msg = c.EXAMPLE_ERR_INVALID_HOST
                raise ValueError(msg)
            if host == c.EXAMPLE_DEFAULT_HOST:
                return host
            try:
                _ = ip_address(host)
                return host
            except ValueError:
                if not c.EXAMPLE_REGEX_DOT.search(host):
                    msg = c.EXAMPLE_ERR_INVALID_HOST
                    raise ValueError(msg) from None
                return host


__all__: list[str] = ["ExamplesFlextCliModelsExamplesDatabase"]

"""CLI service protocols using flext-core foundation patterns.

This module provides CLI-specific protocol aliases using flext-core protocols
as the foundation, following FLEXT architectural standards.

✅ CORRECT - Always use flext-core protocols
❌ FORBIDDEN - Never create new abstract base classes or protocols

English code with Portuguese comments following FLEXT standards.
"""

from __future__ import annotations

from flext_core import FlextProtocols

# =============================================================================
# CLI-SPECIFIC PROTOCOL ALIASES USING FLEXT-CORE FOUNDATION
# =============================================================================

# Protocolos CLI específicos usando FlextProtocols como base
# Mantém compatibilidade enquanto usa padrões centralizados

# CLI Command - usa Application.Handler do flext-core
FlextCliCommandProtocol = FlextProtocols.Application.Handler[dict[str, object], object]

# CLI Service - usa Domain.Service do flext-core
FlextCliServiceProtocol = FlextProtocols.Domain.Service

# CLI Formatter - usa Foundation.Callable com saída string
FlextCliFormatterProtocol = FlextProtocols.Foundation.Callable[str]

# CLI Validator - usa Foundation.Validator do flext-core
FlextCliValidatorProtocol = FlextProtocols.Foundation.Validator[object]

# Repository para CLI - usa Domain.Repository do flext-core
FlextCliRepositoryProtocol = FlextProtocols.Domain.Repository[object]

# Factory para CLI - usa Foundation.Factory do flext-core
FlextCliFactoryProtocol = FlextProtocols.Foundation.Factory[object]

# Connection para CLI - usa Infrastructure.Connection do flext-core
FlextCliConnectionProtocol = FlextProtocols.Infrastructure.Connection

# =============================================================================
# COMPATIBILITY ALIASES - Backward compatibility for existing code
# =============================================================================

# Aliases para compatibilidade com código existente
FlextCliCommandImpl = FlextCliCommandProtocol
FlextCliFormatterImpl = FlextCliFormatterProtocol
FlextCliServiceImpl = FlextCliServiceProtocol
FlextCliValidatorImpl = FlextCliValidatorProtocol

# =============================================================================
# EXPORTS - Public API using flext-core protocols only
# =============================================================================

__all__ = [
    # Main protocol aliases
    "FlextCliCommandProtocol",
    "FlextCliConnectionProtocol",
    "FlextCliFactoryProtocol",
    "FlextCliFormatterProtocol",
    "FlextCliRepositoryProtocol",
    "FlextCliServiceProtocol",
    "FlextCliValidatorProtocol",
    # Compatibility aliases
    "FlextCliCommandImpl",
    "FlextCliFormatterImpl",
    "FlextCliServiceImpl",
    "FlextCliValidatorImpl",
]

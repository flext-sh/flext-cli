"""FLEXT-CLI Performance Optimizations.

This module provides performance optimization utilities including:
- Lazy loading for heavy dependencies
- Command result caching
- Memoization decorators
- Resource pooling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import importlib
import time
from collections.abc import Callable
from typing import Any, TypeVar

from flext_core import FlextLogger, FlextResult, FlextService

T = TypeVar("T")


class FlextCliLazyLoader(FlextService[None]):
    """Lazy loader for heavy dependencies.

    Defers loading of heavy dependencies until they are actually needed,
    improving CLI startup time.

    Example:
        >>> from flext_cli.performance import FlextCliLazyLoader
        >>>
        >>> loader = FlextCliLazyLoader()
        >>>
        >>> # Register lazy module
        >>> loader.register_lazy_module("pandas", "pd")
        >>>
        >>> # Load when needed
        >>> pd_result = loader.load_module("pandas")
        >>> if pd_result.is_success:
        ...     pd = pd_result.unwrap()
        ...     df = pd.DataFrame({"col": [1, 2, 3]})

    """

    def __init__(self, **data: object) -> None:
        """Initialize lazy loader.

        Args:
            **data: Additional service data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._lazy_modules: dict[str, str] = {}
        self._loaded_modules: dict[str, Any] = {}

    def register_lazy_module(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> FlextResult[None]:
        """Register a module for lazy loading.

        Args:
            module_name: Full module name (e.g., "pandas", "rich.console")
            alias: Optional alias for the module

        Returns:
            FlextResult[None]

        Example:
            >>> loader = FlextCliLazyLoader()
            >>> loader.register_lazy_module("pandas", "pd")
            >>> loader.register_lazy_module("numpy", "np")

        """
        try:
            key = alias or module_name
            self._lazy_modules[key] = module_name

            self._logger.debug(
                "Registered lazy module",
                extra={"module_name": module_name, "alias": key},
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to register lazy module: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def load_module(self, key: str) -> FlextResult[Any]:
        """Load a registered lazy module.

        Args:
            key: Module key (name or alias)

        Returns:
            FlextResult containing loaded module

        Example:
            >>> loader = FlextCliLazyLoader()
            >>> loader.register_lazy_module("json")
            >>> json_result = loader.load_module("json")
            >>> if json_result.is_success:
            ...     json = json_result.unwrap()
            ...     data = json.loads('{"key": "value"}')

        """
        try:
            # Return if already loaded
            if key in self._loaded_modules:
                self._logger.debug("Module already loaded", extra={"module_key": key})
                return FlextResult[Any].ok(self._loaded_modules[key])

            # Check if registered
            if key not in self._lazy_modules:
                return FlextResult[Any].fail(
                    f"Module '{key}' not registered for lazy loading"
                )

            module_name = self._lazy_modules[key]

            # Import module
            module = importlib.import_module(module_name)

            # Cache loaded module
            self._loaded_modules[key] = module

            self._logger.info(
                "Loaded lazy module", extra={"module_name": module_name, "key": key}
            )

            return FlextResult[Any].ok(module)

        except ImportError as e:
            error_msg = f"Failed to import module '{key}': {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)
        except Exception as e:
            error_msg = f"Failed to load module: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)

    def is_loaded(self, key: str) -> bool:
        """Check if module is already loaded.

        Args:
            key: Module key

        Returns:
            True if module is loaded, False otherwise

        """
        return key in self._loaded_modules

    def get_loaded_modules(self) -> FlextResult[dict[str, Any]]:
        """Get all loaded modules.

        Returns:
            FlextResult containing dict of loaded modules

        """
        try:
            return FlextResult[dict[str, Any]].ok(self._loaded_modules.copy())
        except Exception as e:
            error_msg = f"Failed to get loaded modules: {e}"
            self._logger.exception(error_msg)
            return FlextResult[dict[str, Any]].fail(error_msg)

    def execute(self) -> FlextResult[None]:
        """Execute lazy loader operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


class FlextCliCache(FlextService[None]):
    """Result caching system for CLI commands.

    Caches command results to avoid expensive recomputations.
    Supports TTL (time-to-live) expiration.

    Example:
        >>> from flext_cli.performance import FlextCliCache
        >>>
        >>> cache = FlextCliCache()
        >>>
        >>> # Cache result
        >>> cache.set("expensive_query", result_data, ttl=60)
        >>>
        >>> # Retrieve cached result
        >>> cached = cache.get("expensive_query")
        >>> if cached.is_success:
        ...     data = cached.unwrap()

    """

    def __init__(self, **data: object) -> None:
        """Initialize cache.

        Args:
            **data: Additional service data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._cache: dict[str, dict[str, object]] = {}

    def set(
        self,
        key: str,
        value: object,
        ttl: int | None = None,
    ) -> FlextResult[None]:
        """Set cache entry.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)

        Returns:
            FlextResult[None]

        Example:
            >>> cache = FlextCliCache()
            >>> cache.set("user_data", {"name": "Alice"}, ttl=300)

        """
        try:
            expiry = time.time() + ttl if ttl else None

            self._cache[key] = {
                "value": value,
                "expiry": expiry,
                "created_at": time.time(),
            }

            self._logger.debug("Cached entry", extra={"cache_key": key, "ttl": ttl})

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to set cache: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def get(self, key: str) -> FlextResult[Any]:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            FlextResult containing cached value or failure if not found/expired

        Example:
            >>> cache = FlextCliCache()
            >>> result = cache.get("user_data")
            >>> if result.is_success:
            ...     data = result.unwrap()

        """
        try:
            if key not in self._cache:
                return FlextResult[Any].fail(f"Cache miss: '{key}' not found")

            entry = self._cache[key]

            # Check expiry
            if entry["expiry"] is not None and time.time() > entry["expiry"]:
                del self._cache[key]
                return FlextResult[Any].fail(f"Cache expired: '{key}'")

            self._logger.debug("Cache hit", extra={"cache_key": key})

            return FlextResult[Any].ok(entry["value"])

        except Exception as e:
            error_msg = f"Failed to get cache: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)

    def delete(self, key: str) -> FlextResult[None]:
        """Delete cache entry.

        Args:
            key: Cache key

        Returns:
            FlextResult[None]

        """
        try:
            if key in self._cache:
                del self._cache[key]
                self._logger.debug("Deleted cache entry", extra={"cache_key": key})

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to delete cache: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def clear(self) -> FlextResult[None]:
        """Clear all cache entries.

        Returns:
            FlextResult[None]

        """
        try:
            count = len(self._cache)
            self._cache.clear()

            self._logger.info("Cleared cache", extra={"entry_count": count})

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to clear cache: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def cleanup_expired(self) -> FlextResult[int]:
        """Remove expired cache entries.

        Returns:
            FlextResult containing count of removed entries

        """
        try:
            current_time = time.time()
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if entry["expiry"] is not None and current_time > entry["expiry"]
            ]

            for key in expired_keys:
                del self._cache[key]

            self._logger.info(
                "Cleaned up expired cache entries",
                extra={"removed_count": len(expired_keys)},
            )

            return FlextResult[int].ok(len(expired_keys))

        except Exception as e:
            error_msg = f"Failed to cleanup cache: {e}"
            self._logger.exception(error_msg)
            return FlextResult[int].fail(error_msg)

    def get_stats(self) -> FlextResult[dict[str, Any]]:
        """Get cache statistics.

        Returns:
            FlextResult containing cache stats

        """
        try:
            stats = {
                "total_entries": len(self._cache),
                "expired_entries": sum(
                    1
                    for entry in self._cache.values()
                    if entry["expiry"] is not None and time.time() > entry["expiry"]
                ),
            }

            return FlextResult[dict[str, Any]].ok(stats)

        except Exception as e:
            error_msg = f"Failed to get cache stats: {e}"
            self._logger.exception(error_msg)
            return FlextResult[dict[str, Any]].fail(error_msg)

    def execute(self) -> FlextResult[None]:
        """Execute cache operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


def memoize(ttl: int | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Memoization decorator for caching function results.

    Args:
        ttl: Time-to-live in seconds (None for no expiration)

    Returns:
        Decorator function

    Example:
        >>> from flext_cli.performance import memoize
        >>>
        >>> @memoize(ttl=60)
        ... def expensive_computation(x, y):
        ...     '''Expensive function.'''
        ...     time.sleep(2)
        ...     return x + y
        >>>
        >>> result = expensive_computation(5, 3)  # Takes 2 seconds
        >>> result2 = expensive_computation(5, 3)  # Instant (cached)

    """
    cache_instance = FlextCliCache()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> T:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{args!s}:{sorted(kwargs.items())!s}"

            # Try to get cached result
            cached_result = cache_instance.get(cache_key)
            if cached_result.is_success:
                return cached_result.unwrap()

            # Compute and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


__all__ = [
    "FlextCliCache",
    "FlextCliLazyLoader",
    "memoize",
]

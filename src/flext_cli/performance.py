"""FLEXT-CLI Performance Optimizations.

Unified performance optimization service providing lazy loading, caching,
memoization, and resource pooling for CLI operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import importlib
import time
from collections.abc import Callable

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
    T,
)


class FlextCliPerformance(FlextService[object]):
    """Unified performance optimization service for CLI operations.

    Provides lazy loading, caching, memoization, and resource pooling
    through a single service interface with nested helper classes.
    Extends FlextService with full flext-core integration.

    Example:
        >>> from flext_cli.performance import FlextCliPerformance
        >>>
        >>> perf = FlextCliPerformance()
        >>>
        >>> # Lazy loading
        >>> perf.lazy_loader.register_lazy_module("pandas", "pd")
        >>> pd_result = perf.lazy_loader.load_module("pandas")
        >>>
        >>> # Caching
        >>> perf.cache.set("expensive_result", data, ttl=60)
        >>> cached = perf.cache.get("expensive_result")
        >>>
        >>> # Memoization
        >>> @perf.memoize(ttl=300)
        ... def expensive_func(x, y):
        ...     return x + y

    """

    def __init__(self, **data: object) -> None:
        """Initialize unified performance service.

        Args:
            **data: Additional service initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)

        # Initialize nested performance components
        self._lazy_loader = self._LazyLoader()
        self._cache = self._Cache()
        self._memoizer = self._Memoizer()

    class _LazyLoader(FlextService[object]):
        """Lazy loader for heavy dependencies.

        Defers loading of heavy dependencies until they are actually needed,
        improving CLI startup time.

        Example:
            >>> perf = FlextCliPerformance()
            >>> perf.lazy_loader.register_lazy_module("pandas", "pd")
            >>> pd_result = perf.lazy_loader.load_module("pandas")

        """

        def __init__(self, **data: object) -> None:
            """Initialize lazy loader.

            Args:
                **data: Additional service data

            """
            super().__init__(**data)
            self._logger = FlextLogger(__name__)
            self._lazy_modules: FlextTypes.StringDict = {}
            self._loaded_modules: FlextTypes.Dict = {}

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

        def load_module(self, key: str) -> FlextResult[object]:
            """Load a registered lazy module.

            Args:
                key: Module key (name or alias)

            Returns:
                FlextResult containing loaded module

            """
            try:
                # Return if already loaded
                if key in self._loaded_modules:
                    self._logger.debug(
                        "Module already loaded", extra={"module_key": key}
                    )
                    return FlextResult[object].ok(self._loaded_modules[key])

                # Check if registered
                if key not in self._lazy_modules:
                    return FlextResult[object].fail(
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

                return FlextResult[object].ok(module)

            except ImportError as e:
                error_msg = f"Failed to import module '{key}': {e}"
                self._logger.exception(error_msg)
                return FlextResult[object].fail(error_msg)
            except Exception as e:
                error_msg = f"Failed to load module: {e}"
                self._logger.exception(error_msg)
                return FlextResult[object].fail(error_msg)

        def is_loaded(self, key: str) -> bool:
            """Check if module is already loaded.

            Args:
                key: Module key

            Returns:
                True if module is loaded, False otherwise

            """
            return key in self._loaded_modules

        def get_loaded_modules(self) -> FlextResult[FlextTypes.Dict]:
            """Get all loaded modules.

            Returns:
                FlextResult containing dict of loaded modules

            """
            try:
                return FlextResult[FlextTypes.Dict].ok(self._loaded_modules.copy())
            except Exception as e:
                error_msg = f"Failed to get loaded modules: {e}"
                self._logger.exception(error_msg)
                return FlextResult[FlextTypes.Dict].fail(error_msg)

        # Attribute declarations - override FlextService optional types
        # These are guaranteed initialized in __init__
        _logger: FlextLogger
        _container: FlextContainer

        def execute(self) -> FlextResult[object]:
            """Execute lazy loader operations.

            Returns:
                FlextResult[None]

            """
            return FlextResult[None].ok(None)

    class _Cache(FlextService[object]):
        """Result caching system for CLI commands.

        Caches command results to avoid expensive recomputations.
        Supports TTL (time-to-live) expiration.

        Example:
            >>> perf = FlextCliPerformance()
            >>> perf.cache.set("expensive_query", result_data, ttl=60)
            >>> cached = perf.cache.get("expensive_query")

        """

        # Attribute declarations - override FlextService optional types
        _logger: FlextLogger
        _container: FlextContainer

        def __init__(self, **data: object) -> None:
            """Initialize cache.

            Args:
                **data: Additional service data

            """
            super().__init__(**data)
            self._logger = FlextLogger(__name__)
            self._cache: FlextTypes.NestedDict = {}

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

        def get(self, key: str) -> FlextResult[object]:
            """Get cached value.

            Args:
                key: Cache key

            Returns:
                FlextResult containing cached value or failure if not found/expired

            """
            try:
                if key not in self._cache:
                    return FlextResult[object].fail(f"Cache miss: '{key}' not found")

                entry = self._cache[key]

                # Check expiry
                if entry["expiry"] is not None and time.time() > entry["expiry"]:
                    del self._cache[key]
                    return FlextResult[object].fail(f"Cache expired: '{key}'")

                self._logger.debug("Cache hit", extra={"cache_key": key})

                return FlextResult[object].ok(entry["value"])

            except Exception as e:
                error_msg = f"Failed to get cache: {e}"
                self._logger.exception(error_msg)
                return FlextResult[object].fail(error_msg)

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

        def get_stats(self) -> FlextResult[FlextTypes.Dict]:
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

                return FlextResult[FlextTypes.Dict].ok(stats)

            except Exception as e:
                error_msg = f"Failed to get cache stats: {e}"
                self._logger.exception(error_msg)
                return FlextResult[FlextTypes.Dict].fail(error_msg)

        def execute(self) -> FlextResult[object]:
            """Execute cache operations.

            Returns:
                FlextResult[None]

            """
            return FlextResult[None].ok(None)

    class _Memoizer:
        """Memoization decorator for caching function results.

        Provides a decorator that caches function results to avoid
        expensive recomputations.

        Example:
            >>> perf = FlextCliPerformance()
            >>> @perf.memoize(ttl=60)
            ... def expensive_func(x, y):
            ...     return x + y

        """

        def __init__(self) -> None:
            """Initialize memoizer with internal cache."""
            self._cache = FlextCliPerformance._Cache()

        def __call__(
            self, ttl: int | None = None
        ) -> Callable[[Callable[..., T]], Callable[..., T]]:
            """Create memoization decorator.

            Args:
                ttl: Time-to-live in seconds (None for no expiration)

            Returns:
                Decorator function

            """

            def decorator(func: Callable[..., T]) -> Callable[..., T]:
                @functools.wraps(func)
                def wrapper(*args: object, **kwargs: object) -> T:
                    # Create cache key from function name and arguments
                    cache_key = f"{func.__name__}:{args!s}:{sorted(kwargs.items())!s}"

                    # Try to get cached result
                    cached_result = self._cache.get(cache_key)
                    if cached_result.is_success:
                        return cached_result.unwrap()

                    # Compute and cache result
                    result = func(*args, **kwargs)
                    self._cache.set(cache_key, result, ttl=ttl)

                    return result

                return wrapper

            return decorator

    # ==========================================================================
    # PUBLIC PROPERTIES - Access to nested performance components
    # ==========================================================================

    @property
    def lazy_loader(self) -> _LazyLoader:
        """Access lazy loading functionality.

        Returns:
            _LazyLoader: Lazy loader instance for module loading

        """
        return self._lazy_loader

    @property
    def cache(self) -> _Cache:
        """Access caching functionality.

        Returns:
            _Cache: Cache instance for result caching

        """
        return self._cache

    @property
    def memoize(self) -> _Memoizer:
        """Access memoization decorator.

        Returns:
            _Memoizer: Memoizer instance for function result caching

        """
        return self._memoizer

    def execute(self) -> FlextResult[object]:
        """Execute performance optimization operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliPerformance",
]

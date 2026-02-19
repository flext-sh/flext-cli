from __future__ import annotations

from pydantic import BaseModel

from flext_core import r

from flext_cli.middleware import (
    LoggingMiddleware,
    RetryMiddleware,
    ValidationMiddleware,
    compose_middleware,
)


class Ctx:
    def __init__(self) -> None:
        self.command = "cmd"
        self.params: dict[str, object] = {}


class Schema(BaseModel):
    value: int


def test_logging_middleware_calls_next() -> None:
    middleware = LoggingMiddleware()
    ctx = Ctx()

    result = middleware(ctx, lambda _ctx: r.ok("ok"))

    assert result.is_success
    assert result.value == "ok"


def test_validation_middleware_success_and_failure_paths() -> None:
    middleware = ValidationMiddleware(Schema)

    ok_ctx = Ctx()
    ok_ctx.params = {"value": 1}
    ok_result = middleware(ok_ctx, lambda _ctx: r.ok("ok"))
    assert ok_result.is_success
    assert ok_ctx.params == {"value": 1}

    bad_ctx = Ctx()
    bad_ctx.params = {"value": "x"}
    bad_result = middleware(bad_ctx, lambda _ctx: r.ok("ok"))
    assert bad_result.is_failure


def test_retry_middleware_paths(monkeypatch) -> None:
    monkeypatch.setattr("flext_cli.middleware.time.sleep", lambda _delay: None)
    middleware = RetryMiddleware(max_retries=3, backoff=0.0)
    ctx = Ctx()

    immediate = middleware(ctx, lambda _ctx: r.ok("ok"))
    assert immediate.is_success

    attempts = {"count": 0}

    def eventually(_ctx: Ctx):
        attempts["count"] += 1
        if attempts["count"] < 2:
            return r.fail("fail")
        return r.ok("done")

    retried = middleware(ctx, eventually)
    assert retried.is_success
    assert retried.value == "done"

    always_fail = RetryMiddleware(max_retries=2, backoff=0.0)
    failed = always_fail(ctx, lambda _ctx: r.fail("nope"))
    assert failed.is_failure


def test_compose_middleware_chains_in_order() -> None:
    events: list[str] = []

    def m1(ctx: Ctx, next_):
        events.append("m1")
        return next_(ctx)

    def m2(ctx: Ctx, next_):
        events.append("m2")
        return next_(ctx)

    def handler(_ctx: Ctx):
        events.append("handler")
        return r.ok("ok")

    composed = compose_middleware([m1, m2], handler)
    result = composed(Ctx())

    assert result.is_success
    assert events == ["m1", "m2", "handler"]

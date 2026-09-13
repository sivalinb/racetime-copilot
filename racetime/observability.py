"""Best-effort hosted spans with explicit inputs and sanitized failures."""

import inspect
import os
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache, wraps

import langsmith as ls

_current = ContextVar("racetime_observability_span", default=None)


def provider():
    return os.getenv("RACETIME_OBSERVABILITY", "langsmith").lower()


def current_span():
    return _current.get()


@lru_cache(maxsize=1)
def braintrust_logger():
    import braintrust

    if not os.getenv("BRAINTRUST_API_KEY"):
        raise ValueError("BRAINTRUST_API_KEY is missing.")
    return braintrust.init_logger(
        project_id=os.getenv("BRAINTRUST_PROJECT_ID") or None,
        project=None
        if os.getenv("BRAINTRUST_PROJECT_ID")
        else os.getenv("BRAINTRUST_PROJECT", "racetime-copilot"),
        api_key=os.environ["BRAINTRUST_API_KEY"],
    )


class BraintrustRun:
    """Small facade so existing explicit span logging supports either service."""

    def __init__(self, span, parent=None):
        self.span = span
        self.id = span.id
        self.trace_id = parent.trace_id if parent else self.id
        self.outputs = {}

    def end(self, outputs=None, error=None):
        if outputs:
            self.outputs.update(outputs)
            metrics = self.outputs.get("usage_metadata", {})
            self.span.log(
                output=self.outputs,
                metrics={
                    name: metrics[key]
                    for name, key in (
                        ("prompt_tokens", "input_tokens"),
                        ("completion_tokens", "output_tokens"),
                        ("tokens", "total_tokens"),
                    )
                    if isinstance(metrics.get(key), (int, float))
                },
            )
        if error:
            self.span.log(error=error)

    def add_metadata(self, values):
        self.span.log(metadata=values)

    def get_url(self):
        return self.span.link()


@contextmanager
def braintrust_span(name, run_type, inputs, meta):
    raw = None
    run = None
    parent = current_span()
    try:
        logger = braintrust_logger()
        source = parent.span if isinstance(parent, BraintrustRun) else logger
        kind = (
            "llm"
            if run_type in ("llm", "embedding")
            else "tool"
            if run_type in ("tool", "retriever")
            else "task"
        )
        raw = source.start_span(
            name=name,
            type=kind,
            input=inputs or {},
            metadata={"run_type": run_type, **(meta or {})},
        )
        run = BraintrustRun(raw, parent)
    except Exception:
        raw = None
    token = _current.set(run)
    try:
        yield run
    except BaseException:
        if run:
            try:
                run.end(error="Operation failed; see sanitized local error.")
            except Exception:
                pass
        raise
    finally:
        _current.reset(token)
        if raw:
            try:
                raw.end()
            except Exception:
                pass


def enabled():
    return (
        provider() == "langsmith"
        and os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        and bool(os.getenv("LANGSMITH_API_KEY"))
    )


@contextmanager
def span(name, run_type="chain", inputs=None, metadata=None):
    """Telemetry setup/transport failures must not change application results."""
    if provider() == "braintrust":
        with braintrust_span(name, run_type, inputs, metadata) as run:
            yield run
        return
    manager = None
    run = None
    if enabled():
        try:
            manager = ls.trace(
                name,
                run_type=run_type,
                inputs=inputs or {},
                metadata=metadata or {},
                project_name=os.getenv("LANGSMITH_PROJECT", "racetime-copilot"),
                tags=["racetime", "video-workspace"],
            )
            run = manager.__enter__()
        except Exception:
            manager = None
    token = _current.set(run)
    try:
        yield run
    except BaseException:
        if run is not None:
            # SDK errors may contain signed URLs or credentials. Keep them local.
            try:
                run.end(error="Operation failed; see the sanitized local job error.")
            except Exception:
                pass
        raise
    finally:
        _current.reset(token)
        if manager is not None:
            try:
                manager.__exit__(None, None, None)
            except Exception:
                pass


def record(run, outputs):
    if run is not None:
        try:
            run.end(outputs={**(run.outputs or {}), **outputs})
        except Exception:
            pass


def metadata(run, values):
    if run is not None:
        try:
            run.add_metadata(values)
        except Exception:
            pass


def observed(name, run_type, keys, output=None):
    """Only named arguments cross the tracing boundary; never self/media bytes."""

    def decorate(fn):
        signature = inspect.signature(fn)

        @wraps(fn)
        def wrapped(*args, **kwargs):
            values = signature.bind(*args, **kwargs)
            values.apply_defaults()
            inputs = {k: values.arguments[k] for k in keys}
            with span(name, run_type, inputs) as run:
                result = fn(*args, **kwargs)
                serialized = output(result) if output else result
                if hasattr(serialized, "model_dump"):
                    serialized = serialized.model_dump()
                record(run, {"result": serialized})
                return result

        return wrapped

    return decorate


def trace_reference(run):
    if run is None:
        return {}
    reference = {
        "trace_id": str(run.trace_id),
        "run_id": str(run.id),
        "provider": "braintrust" if isinstance(run, BraintrustRun) else "langsmith",
        "project": os.getenv("BRAINTRUST_PROJECT", "racetime-copilot")
        if isinstance(run, BraintrustRun)
        else os.getenv("LANGSMITH_PROJECT", "racetime-copilot"),
        "status": "submitted; ingestion is not confirmed by the app",
    }
    if isinstance(run, BraintrustRun):
        reference["root_run_id"] = reference.pop("trace_id")
    try:
        reference["url"] = run.get_url()
    except Exception:
        pass
    return reference

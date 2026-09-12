"""Best-effort LangSmith spans with explicit inputs and sanitized failures."""

import inspect
import os
from contextlib import contextmanager
from functools import wraps

import langsmith as ls


def enabled():
    return os.getenv("LANGSMITH_TRACING", "false").lower() == "true" and bool(
        os.getenv("LANGSMITH_API_KEY")
    )


@contextmanager
def span(name, run_type="chain", inputs=None, metadata=None):
    """Telemetry setup/transport failures must not change application results."""
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
        "project": os.getenv("LANGSMITH_PROJECT", "racetime-copilot"),
        "status": "submitted; ingestion is not confirmed by the app",
    }
    try:
        reference["url"] = run.get_url()
    except Exception:
        pass
    return reference

from typing import Any

from object_trace.object_trace import Tracer


def trace(x: Any, label: str = "") -> Any:
    """Start tracing the object `x`, if tracing is active."""
    if Tracer.ACTIVE_TRACER is not None:
        Tracer.ACTIVE_TRACER.add_object(x, label)
    return x

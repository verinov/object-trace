from typing import Any
import contextlib
import itertools

from object_trace.object_trace import Tracer


def trace(x: Any, labe: str = "") -> Any:
    """Start tracing the object `x`, if tracing is active."""
    if Tracer.ACTIVE_TRACER is not None:
        Tracer.ACTIVE_TRACER.add_object(x, labe)
    return x


@contextlib.contextmanager
def print_traces():
    with Tracer() as traces:
        yield

    for t in traces:
        print(f"# Trace for label=`{t.label}`")
        for line, _ in itertools.groupby(t.format_lines()):
            print(line)
        print("-" * 80)

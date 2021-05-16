import collections
import dataclasses
import inspect
import sys
import gc
import threading
from typing import List, Optional, Set, Callable, Iterator
from types import CodeType
from warnings import warn

from .py_stack import get_stack_top_id


def _empty_handler(frame, event_type, arg):
    return None


def _default_frame_filter(frame):
    return True


@dataclasses.dataclass
class Event:
    call: "Call"
    line_no: int

    @property
    def info(self):
        raise NotImplementedError(self)


@dataclasses.dataclass
class CountEvent(Event):
    old_refcount: int
    new_refcount: int

    @property
    def info(self):
        return f"Ref count {self.old_refcount}->{self.new_refcount}"


@dataclasses.dataclass
class UseEvent(Event):
    @property
    def info(self):
        return "use"


class Trace:
    id_: int
    label: str
    frame_filter: Callable  # TODO
    closed: bool
    log: List[Event]

    def __init__(self, id_, label, frame_filter):
        self.id_ = id_
        self.label = label
        self.frame_filter = frame_filter
        self.closed = False
        self.log = []

    def close(self):
        self.closed = True

    def count_change(self, call, line_no, old_refcount, new_refcount) -> None:
        if self.closed:
            return

        self.log.append(CountEvent(call, line_no, old_refcount, new_refcount))

    def use(self, call: "Call", line_no: int) -> None:
        if self.closed:
            return

        self.log.append(UseEvent(call, line_no))

    def format_lines(self) -> Iterator[str]:
        old_stacktrace: List["Call"] = []
        TAB = "  "

        def matching_prefix_size(s1, s2):
            n = 0
            for x1, x2 in zip(s1, s2):
                if x1 is x2:
                    n += 1
                else:
                    break
            return n

        def format_line(
            depth: int, line_no: Optional[int], info: str, source_line: str
        ):
            s = f"{'_' if line_no is None else line_no:<4}: {info}"
            return "".join(
                [TAB * depth, s, " " * (40 - len(s)), "| ", source_line.strip()]
            )

        for record in self.log:
            new_call_stack = record.call.stacktrace
            depth = matching_prefix_size(old_stacktrace, new_call_stack)

            while depth < len(new_call_stack):
                call = new_call_stack[depth]
                code = call.code
                _, first_line_no = inspect.getsourcelines(code)

                yield format_line(
                    depth,
                    call.parent_lineno,
                    f"call `{code.co_name}`",
                    call.caller_source_line,
                )
                depth += 1
                yield TAB * depth + f"[{code.co_filename}:{first_line_no}]"

            yield format_line(
                depth,
                record.line_no,
                record.info,
                record.call.get_source_line(record.line_no),
            )

            old_stacktrace = new_call_stack


@dataclasses.dataclass
class Call:
    code: CodeType
    parent: Optional["Call"]
    traces: Set[Trace]
    parent_lineno: Optional[int]
    _stacktrace: Optional[List["Call"]] = None

    def get_source_line(self, line_no: Optional[int] = None) -> str:
        source_lines, first_line_no = inspect.getsourcelines(self.code)
        line_index = 0 if line_no is None else line_no - first_line_no
        if line_index >= len(source_lines):
            source_lines = open(self.code.co_filename, "r").readlines()

        return source_lines[line_index]

    @property
    def caller_source_line(self) -> str:
        if self.parent is None:
            return ""
        else:
            return self.parent.get_source_line(self.parent_lineno)

    @property
    def stacktrace(self) -> List["Call"]:
        if self._stacktrace is None:
            if self.parent is None:
                self._stacktrace = [self]
            else:
                self._stacktrace = [*self.parent.stacktrace, self]
        return self._stacktrace


class Tracer:
    all_traces: List[Trace]

    ACTIVE_TRACER = None  # singleton, because there is only one `sys.settrace`

    def __init__(self):
        self._trace_handlers = {
            "call": self._trace_call,
            "line": self._trace_line,
            "opcode": self._trace_opcode,
            "return": self._trace_return,
            "exception": _empty_handler,
            "c_call": _empty_handler,
            "c_return": _empty_handler,
            "c_exception": _empty_handler,
        }

        # delay import, because `trace` depends on `Tracer`
        from object_trace import trace

        self._exclude_codes = {
            f.__code__
            for f in [
                threading.settrace,
                inspect.currentframe,
                trace,
                _default_frame_filter,
                *[
                    f
                    for v in globals().values()
                    if inspect.isclass(v)
                    for _, f in inspect.getmembers(v, inspect.isfunction)
                ],
            ]
        }

        # id(x) -> x, to keep them alive
        self._objects = {}
        # id(x) -> refcount(x), to report the changes in ref count
        self._refcounts = {}
        # id(x) -> Set[Trace], because the same object might be traces more than once
        self._traces = collections.defaultdict(set)
        # live_frame -> Call
        self._live_calls = {None: None}

        self.all_traces = []

    def __enter__(self):
        if Tracer.ACTIVE_TRACER is not None:
            warn("There is already a Tracer active, doing nothing.", RuntimeWarning)
            return

        Tracer.ACTIVE_TRACER = self

        sys.settrace(self._trace_any)
        threading.settrace(self._trace_any)
        return self.all_traces

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Tracer.ACTIVE_TRACER is not self:
            return

        # put the final state in traces
        self._trace_line(sys._getframe(1), "line", None)

        sys.settrace(None)
        threading.settrace(None)
        Tracer.ACTIVE_TRACER = None

    def _get_call(self, frame) -> Call:
        try:
            return self._live_calls[frame]
        except KeyError:
            pass

        assert frame.f_code not in self._exclude_codes, "Tracing inside object_trace"

        frame.f_trace = self._trace_any

        traces = {
            trace
            for traces in self._traces.values()
            for trace in traces
            if trace.frame_filter(frame)
        }
        parent_lineno = None if frame.f_back is None else frame.f_back.f_lineno
        call = self._live_calls[frame] = Call(
            frame.f_code, self._get_call(frame.f_back), traces, parent_lineno
        )
        return call

    def _get_refcount(self, id_):
        return sys.getrefcount(self._objects[id_]) - 2

    def add_object(self, x, label: str, frame_filter=_default_frame_filter):
        id_ = id(x)
        self._objects[id_] = x

        del x
        gc.collect()
        self._refcounts[id_] = self._get_refcount(id_)

        trace = Trace(id_, label, frame_filter)
        self._traces[id_].add(trace)
        self.all_traces.append(trace)

        for frame, call in self._live_calls.items():
            if frame is None:
                continue

            if trace.frame_filter(frame):
                frame.f_trace_lines = True
                frame.f_trace_opcodes = True
                call.traces.add(trace)

        return self._objects[id_]

    def _trace_any(self, frame, event_type, arg):
        return self._trace_handlers[event_type](frame, event_type, arg)

    def _trace_call(self, frame, event_type, arg):
        if frame.f_code in self._exclude_codes:
            return _empty_handler
        else:
            frame.f_trace_lines = frame.f_trace_opcodes = bool(
                self._get_call(frame).traces
            )
            return self._trace_any

    def _trace_return(self, frame, event_type, arg):
        if event_type == "return":
            self._trace_line(frame, None, None)
            self._live_calls.pop(frame, None)
        # return value is ignored

    def _trace_line(self, frame, event_type, arg):
        gc.collect()
        for id_ in list(self._traces):
            old_refcount = self._refcounts[id_]
            new_refcount = self._get_refcount(id_)
            if old_refcount == new_refcount:
                continue

            self._refcounts[id_] = new_refcount

            call = self._get_call(frame)
            line_no = frame.f_lineno
            for trace in self._traces[id_] & call.traces:
                trace.count_change(call, line_no, old_refcount, new_refcount)
            if new_refcount == 0:
                # clean up
                for trace in self._traces.pop(id_):
                    trace.close()
                del self._refcounts[id_]
                del self._objects[id_]

        return self._trace_any

    def _trace_opcode(self, frame, event_type, arg):
        top_id = get_stack_top_id(frame)
        if top_id in self._traces:
            call = self._get_call(frame)
            line_no = frame.f_lineno
            for trace in self._traces[top_id] & self._get_call(frame).traces:
                trace.use(call, line_no)

        return self._trace_any

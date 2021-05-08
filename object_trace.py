import sys
import gc
import dataclasses
import collections
import threading
from typing import NamedTuple, Tuple, Set, Optional, List
import inspect
from warnings import warn

from py_stack import get_stack_top_id


def trace(x, label: str = ""):
    if Tracer.ACTIVE_PROFILER is not None:
        Tracer.ACTIVE_PROFILER.add_object(x, label, inspect.currentframe().f_back)
    return x


def _default_handler(frame, event_type, arg):
    print("Default handler for ", event_type)
    return None


def _stop_local_tracing(*args):
    return None  # No-op


@dataclasses.dataclass
class Event:
    call: "Call"
    line_no: int

    @property
    def source_line(self):
        source_lines, first_line_no = inspect.getsourcelines(self.call.code)
        return source_lines[self.line_no - first_line_no]


@dataclasses.dataclass
class CountEvent(Event):
    old_refcount: int
    new_refcount: int

    def __repr__(self):
        return f"{self.line_no:<4}: count {self.old_refcount}->{self.new_refcount}"


@dataclasses.dataclass
class UseEvent(Event):
    def __repr__(self):
        return f"{self.line_no:<4}: use"


class Trace:
    id_: int
    label: str
    frame_filter: None  # TODO
    closed: bool
    log: list

    def __init__(self, id_, label, frame_filter):
        self.id_ = id_
        self.label = label
        self.frame_filter = frame_filter
        self.closed = False
        self.log = []

    def close(self):
        self.closed = True

    def count_change(self, call, line_no, old_refcount, new_refcount):
        if self.closed:
            return

        self.log.append(CountEvent(call, line_no, old_refcount, new_refcount))

    def use(self, call, line_no):
        self.log.append(UseEvent(call, line_no))

    def format(self, output):
        tab = "  "
        old_stacktrace = []

        for record in self.log:
            new_call_stack = record.call.stacktrace

            depth = 0

            for old_call, new_call in zip(old_stacktrace, new_call_stack):
                if old_call is new_call:
                    depth += 1
                else:
                    break

            while depth < len(new_call_stack):
                code = new_call_stack[depth].code
                _, first_line_no = inspect.getsourcelines(code)
                output.write(tab * depth)
                output.write(f"{code.co_filename}:{first_line_no} ({code.co_name})\n")
                depth += 1

            s = tab * depth + str(record)

            output.write(
                "".join(
                    [s, " " * (40 - len(s)), "| ", record.source_line.strip(), "\n"]
                )
            )

            old_stacktrace = new_call_stack


@dataclasses.dataclass
class Call:
    code: "code"
    parent: Optional["Call"]
    traces: Set[Trace]
    _stacktrace: Optional[List["Call"]] = None

    @property
    def stacktrace(self) -> List["Call"]:
        if self._stacktrace is None:
            if self.parent is None:
                self._stacktrace = [self]
            else:
                self._stacktrace = [*self.parent.stacktrace, self]
        return self._stacktrace


class Tracer:
    ACTIVE_PROFILER = None  # singleton

    def __init__(self):
        self._trace_handlers = {
            "call": self._trace_call,
            "line": self._trace_line,
            "opcode": self._trace_opcode,
            "return": self._trace_return,
            "exception": _default_handler,
            "c_call": _default_handler,
            "c_return": _default_handler,
            "c_exception": _default_handler,
        }

        self._exclude_codes = {
            f.__code__
            for f in [
                threading.settrace,
                inspect.currentframe,
                # trace,
                # _default_handler,
                # *[f for _, f in inspect.getmembers(Tracer, inspect.isfunction)],
                # *[f for _, f in inspect.getmembers(Trace, inspect.isfunction)],
            ]
        }

        # id(x) -> x
        self._objects = {}
        # id(x) -> refcount(x)
        self._refcounts = {}
        # id(x) -> Set[Trace]
        self._traces = collections.defaultdict(set)
        # live_frame -> Call
        self._live_calls = {None: None}

        self.all_traces = []

    def __enter__(self):
        if Tracer.ACTIVE_PROFILER is not None:
            warn("There is already a Tracer active, doing nothing.", RuntimeWarning)
            return

        Tracer.ACTIVE_PROFILER = self

        sys.settrace(self._trace_any)
        threading.settrace(self._trace_any)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Tracer.ACTIVE_PROFILER is not self:
            return

        sys.settrace(None)
        threading.settrace(None)
        Tracer.ACTIVE_PROFILER = None

    def _get_call(self, frame) -> Call:
        try:
            return self._live_calls[frame]
        except KeyError:
            pass

        traces = {
            trace
            for traces in self._traces.values()
            for trace in traces
            if trace.frame_filter(frame)
        }

        call = self._live_calls[frame] = Call(
            frame.f_code, self._get_call(frame.f_back), traces
        )
        return call

    def add_object(self, x, label: str, frame, frame_filter=lambda frame: True):
        id_ = id(x)
        self._objects[id_] = x
        self._refcounts[id_] = len(gc.get_referrers(x)) - 1

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

        return x

    def _trace_any(self, frame, event_type, arg):
        return self._trace_handlers[event_type](frame, event_type, arg)

    def _trace_call(self, frame, event_type, arg):
        if frame.f_code.co_filename == __file__ or frame.f_code in self._exclude_codes:
            return None

        frame.f_trace_lines = frame.f_trace_opcodes = bool(self._get_call(frame).traces)
        return self._trace_any

    def _trace_return(self, frame, event_type, arg):
        self._live_calls.pop(frame, None)
        # return value is ignored

    def _trace_line(self, frame, event_type, arg):
        for id_ in list(self._traces):
            old_refcount = self._refcounts[id_]
            new_refcount = len(gc.get_referrers(self._objects[id_])) - 1

            if old_refcount != new_refcount:
                call = self._get_call(frame)
                line_no = frame.f_lineno - 1
                for trace in self._traces[id_] & call.traces:
                    trace.count_change(call, line_no, old_refcount, new_refcount)

            if new_refcount == 0:
                # clean up
                for trace in self._traces.pop(id_):
                    trace.close()
                del self._refcounts[id_]
                del self._objects[id_]

            else:
                self._refcounts[id_] = new_refcount

        return self._trace_any

    def _trace_opcode(self, frame, event_type, arg):
        top_id = get_stack_top_id(frame)
        if top_id in self._traces:
            call = self._get_call(frame)
            line_no = frame.f_lineno
            for trace in self._traces[top_id] & self._get_call(frame).traces:
                trace.use(call, line_no)

        return self._trace_any

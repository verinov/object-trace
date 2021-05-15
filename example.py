from object_trace import trace, Tracer
import itertools

import glob

a = []


def f():
    global a
    a.append(1)
    a = []


with Tracer() as traces:
    trace(a, "list")
    glob.glob(trace("./*", "glob"))
    f()

for t in traces:
    print(f"# Trace for label=`{t.label}`")
    for line, _ in itertools.groupby(t.format_lines()):
        print(line)
    print("-" * 80)

from object_trace import trace, Tracer
from sys import stdout

data = {}


def f2(x):
    return x


def func():
    a = [1, 2, 3, 4]
    trace(a, "a")
    data["a"] = trace(3, "3")
    data["b"] = a
    a = 11
    data["b"] = 3
    data["a"] = trace(3, "3")
    2 + 4
    str(3) + str(3 + 1)
    "a"
    data["c"] = data["a"]


with Tracer() as tt:
    func()

for trace in tt.all_traces:
    print(f"# Trace for label={trace.label}")

    trace.format(stdout)

    print("-" * 80)

print("Done")

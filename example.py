from object_trace import trace, Tracer
from sys import stdout

data = {}


def f2(x):
    return x


def func():
    a = [1, 2, 3, 4]
    trace(a, label="a")
    data["a"] = trace(3, label="3")
    data["b"] = f2(a)
    a = 11
    data["b"] = f2(3)
    data["a"] = trace(3, label="3")
    2 + 4
    str(3) + str(3 + 1)
    "a"
    data["c"] = data["a"]


with Tracer() as tt:
    func()
    x = data["b"]
    x = x + x

for t in tt.all_traces:
    print(f"# Trace for label=`{t.label}`")
    t.format(stdout)
    print("-" * 80)

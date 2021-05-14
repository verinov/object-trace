from object_trace import trace, Tracer
from sys import stdout

import glob

with Tracer() as traces:
    glob.glob(trace("./*", "glob"))

for t in traces:
    print(f"# Trace for label=`{t.label}`")
    t.format(stdout)
    print("-" * 80)

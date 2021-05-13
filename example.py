from object_trace import trace, Tracer
from sys import stdout

import glob

with Tracer() as tt:
    glob.glob(trace("./*", "glob"))

for t in tt.all_traces:
    print(f"# Trace for label=`{t.label}`")
    t.format(stdout)
    print("-" * 80)

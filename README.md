Trace every use of selected objects.

# Install
```
pip install object-trace
```

# Example result
Given the following [script](example.py)
```
from object_trace import trace, print_traces

def producer_of_X(cache):
    cache["X"] = trace(42.42, "X")

def inscrutable_user_of_X(cache):
    cache["Y"] = cache["X"] + 1
    cache["X"] = 15.1

with print_traces():
    d = {}
    producer_of_X(d)
    inscrutable_user_of_X(d)
    print(d["X"])
```

running `python3.9 example.py` prints:
```
# Trace for label=`X`
_   : call `<module>`                   | 
  [/mnt/c/Users/alexv/repos/object_trace/example.py:1]
  15  : call `producer_of_X`              | producer_of_X(d)
    [/mnt/c/Users/alexv/repos/object_trace/example.py:4]
    5   : use                               | cache["X"] = trace(42.42, "X")
    5   : Ref count 6->3                    | cache["X"] = trace(42.42, "X")
  16  : call `inscrutable_user_of_X`      | inscrutable_user_of_X(d)
    [/mnt/c/Users/alexv/repos/object_trace/example.py:8]
    9   : use                               | cache["Y"] = cache["X"] + 1
    10  : Ref count 3->2                    | cache["X"] = 15.1
--------------------------------------------------------------------------------
```

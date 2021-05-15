Trace every use of selected objects.

# Install
```
pip install object-trace
```

# Example result
Given the following [script](example.py)
```
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
```

running `python3.9 example.py` prints:
```
# Trace for label=`list`
_   : call `<module>`                   | 
  [/mnt/c/Users/alexv/repos/object_trace/example.py:1]
  16  : use                               | trace(a, "list")
  17  : Ref count 6->1                    | glob.glob(trace("./*", "glob"))
  18  : call `f`                          | f()
    [/mnt/c/Users/alexv/repos/object_trace/example.py:9]
    11  : use                               | a.append(1)
  18  : Ref count 1->0                    | f()
--------------------------------------------------------------------------------
# Trace for label=`glob`
_   : call `<module>`                   | 
  [/mnt/c/Users/alexv/repos/object_trace/example.py:1]
  17  : use                               | glob.glob(trace("./*", "glob"))
  17  : call `glob`                       | glob.glob(trace("./*", "glob"))
    [/usr/lib/python3.9/glob.py:10]
    21  : Ref count 7->5                    | return list(iglob(pathname, recursive=recursive))
    21  : use                               | return list(iglob(pathname, recursive=recursive))
    21  : call `iglob`                      | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:23]
      34  : Ref count 5->8                    | sys.audit("glob.glob", pathname, recursive)
      34  : use                               | sys.audit("glob.glob", pathname, recursive)
      35  : use                               | it = _iglob(pathname, recursive, False)
      36  : Ref count 8->9                    | if recursive and _isrecursive(pathname):
    21  : call `_iglob`                     | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:41]
      42  : Ref count 9->7                    | dirname, basename = os.path.split(pathname)
      42  : use                               | dirname, basename = os.path.split(pathname)
      42  : call `split`                      | dirname, basename = os.path.split(pathname)
        [/usr/lib/python3.9/posixpath.py:100]
        103 : Ref count 7->10                   | p = os.fspath(p)
        103 : use                               | p = os.fspath(p)
        104 : use                               | sep = _get_sep(p)
        104 : call `_get_sep`                   | sep = _get_sep(p)
          [/usr/lib/python3.9/posixpath.py:41]
          42  : Ref count 10->13                  | if isinstance(path, bytes):
          42  : use                               | if isinstance(path, bytes):
        105 : Ref count 13->10                  | i = p.rfind(sep) + 1
        105 : use                               | i = p.rfind(sep) + 1
        106 : use                               | head, tail = p[:i], p[i:]
      43  : Ref count 10->7                   | if not has_magic(pathname):
      43  : use                               | if not has_magic(pathname):
      43  : call `has_magic`                  | if not has_magic(pathname):
        [/usr/lib/python3.9/glob.py:147]
        148 : Ref count 7->10                   | if isinstance(s, bytes):
        148 : use                               | if isinstance(s, bytes):
        151 : use                               | match = magic_check.search(s)
        152 : Ref count 10->11                  | return match is not None
      53  : Ref count 11->7                   | if not dirname:
      62  : use                               | if dirname != pathname and has_magic(dirname):
  18  : Ref count 7->2                    | f()
--------------------------------------------------------------------------------
```

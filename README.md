Trace every use of selected objects.

# Install
```
pip install object-trace
```

# Example result
Given the following [script](example.py)
```
from object_trace import trace, Tracer
from sys import stdout

import glob

with Tracer() as traces:
    glob.glob(trace("./*", "glob"))

for t in traces:
    print(f"# Trace for label=`{t.label}`")
    t.format(stdout)
    print("-" * 80)
```

running `python3.9 example.py` prints:
```
# Trace for label=`glob`
_   : call `<module>`                   | 
  [/mnt/c/Users/alexv/repos/object_trace/example.py:1]
  7   : use                               | glob.glob(trace("./*", "glob"))
  7   : call `glob`                       | glob.glob(trace("./*", "glob"))
    [/usr/lib/python3.9/glob.py:10]
    21  : Ref count 10->11                  | return list(iglob(pathname, recursive=recursive))
    21  : use                               | return list(iglob(pathname, recursive=recursive))
    21  : call `iglob`                      | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:23]
      34  : Ref count 11->14                  | sys.audit("glob.glob", pathname, recursive)
      34  : use                               | sys.audit("glob.glob", pathname, recursive)
      35  : use                               | it = _iglob(pathname, recursive, False)
      36  : Ref count 14->15                  | if recursive and _isrecursive(pathname):
    21  : call `_iglob`                     | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:41]
      42  : Ref count 15->13                  | dirname, basename = os.path.split(pathname)
      42  : use                               | dirname, basename = os.path.split(pathname)
      42  : call `split`                      | dirname, basename = os.path.split(pathname)
        [/usr/lib/python3.9/posixpath.py:100]
        103 : Ref count 13->16                  | p = os.fspath(p)
        103 : use                               | p = os.fspath(p)
        103 : use                               | p = os.fspath(p)
        104 : use                               | sep = _get_sep(p)
        104 : call `_get_sep`                   | sep = _get_sep(p)
          [/usr/lib/python3.9/posixpath.py:41]
          42  : Ref count 16->19                  | if isinstance(path, bytes):
          42  : use                               | if isinstance(path, bytes):
        105 : Ref count 19->16                  | i = p.rfind(sep) + 1
        105 : use                               | i = p.rfind(sep) + 1
        105 : use                               | i = p.rfind(sep) + 1
        106 : use                               | head, tail = p[:i], p[i:]
        106 : use                               | head, tail = p[:i], p[i:]
      43  : Ref count 16->13                  | if not has_magic(pathname):
      43  : use                               | if not has_magic(pathname):
      43  : call `has_magic`                  | if not has_magic(pathname):
        [/usr/lib/python3.9/glob.py:147]
        148 : Ref count 13->16                  | if isinstance(s, bytes):
        148 : use                               | if isinstance(s, bytes):
        151 : use                               | match = magic_check.search(s)
        152 : Ref count 16->17                  | return match is not None
      53  : Ref count 17->13                  | if not dirname:
      62  : use                               | if dirname != pathname and has_magic(dirname):
--------------------------------------------------------------------------------
```

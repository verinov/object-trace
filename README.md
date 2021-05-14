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
    21  : Ref count 1->3                    | return list(iglob(pathname, recursive=recursive))
    21  : use                               | return list(iglob(pathname, recursive=recursive))
    21  : call `iglob`                      | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:23]
      34  : use                               | sys.audit("glob.glob", pathname, recursive)
      35  : use                               | it = _iglob(pathname, recursive, False)
      36  : Ref count 3->5                    | if recursive and _isrecursive(pathname):
    21  : call `_iglob`                     | return list(iglob(pathname, recursive=recursive))
      [/usr/lib/python3.9/glob.py:41]
      42  : Ref count 5->4                    | dirname, basename = os.path.split(pathname)
      42  : use                               | dirname, basename = os.path.split(pathname)
      42  : call `split`                      | dirname, basename = os.path.split(pathname)
        [/usr/lib/python3.9/posixpath.py:100]
        103 : use                               | p = os.fspath(p)
        103 : use                               | p = os.fspath(p)
        104 : use                               | sep = _get_sep(p)
        104 : call `_get_sep`                   | sep = _get_sep(p)
          [/usr/lib/python3.9/posixpath.py:41]
          42  : use                               | if isinstance(path, bytes):
        105 : use                               | i = p.rfind(sep) + 1
        105 : use                               | i = p.rfind(sep) + 1
        106 : use                               | head, tail = p[:i], p[i:]
        106 : use                               | head, tail = p[:i], p[i:]
      43  : use                               | if not has_magic(pathname):
      43  : call `has_magic`                  | if not has_magic(pathname):
        [/usr/lib/python3.9/glob.py:147]
        148 : use                               | if isinstance(s, bytes):
        151 : use                               | match = magic_check.search(s)
      62  : use                               | if dirname != pathname and has_magic(dirname):
      66  : Ref count 4->5                    | if has_magic(basename):
--------------------------------------------------------------------------------
```

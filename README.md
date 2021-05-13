Trace every use of selected objects.

# Install
```
pip install object-trace
```

# Example result
Running `python example.py` prints the following:
```
# Trace for label=`glob`
_   : call `<module>` (object_trace/example.py:1)| 
  7   : use                               | glob.glob(trace("./*", "glob"))
  7   : call `glob` (/home/verinov/anaconda3/lib/python3.8/glob.py:10)| glob.glob(trace("./*", "glob"))
    20  : RC 2->4                           | """
    21  : use                               | return list(iglob(pathname, recursive=recursive))
    21  : call `iglob` (/home/verinov/anaconda3/lib/python3.8/glob.py:23)| return list(iglob(pathname, recursive=recursive))
      34  : use                               | sys.audit("glob.glob", pathname, recursive)
      35  : use                               | it = _iglob(pathname, recursive, False)
      35  : RC 4->6                           | it = _iglob(pathname, recursive, False)
    21  : call `_iglob` (/home/verinov/anaconda3/lib/python3.8/glob.py:41)| return list(iglob(pathname, recursive=recursive))
      41  : RC 6->5                           | def _iglob(pathname, recursive, dironly):
      42  : use                               | dirname, basename = os.path.split(pathname)
      42  : call `split` (/home/verinov/anaconda3/lib/python3.8/posixpath.py:100)| dirname, basename = os.path.split(pathname)
        103 : use                               | p = os.fspath(p)
        103 : use                               | p = os.fspath(p)
        104 : use                               | sep = _get_sep(p)
        104 : call `_get_sep` (/home/verinov/anaconda3/lib/python3.8/posixpath.py:41)| sep = _get_sep(p)
          42  : use                               | if isinstance(path, bytes):
        105 : use                               | i = p.rfind(sep) + 1
        105 : use                               | i = p.rfind(sep) + 1
        106 : use                               | head, tail = p[:i], p[i:]
        106 : use                               | head, tail = p[:i], p[i:]
      43  : use                               | if not has_magic(pathname):
      43  : call `has_magic` (/home/verinov/anaconda3/lib/python3.8/glob.py:147)| if not has_magic(pathname):
        148 : use                               | if isinstance(s, bytes):
        151 : use                               | match = magic_check.search(s)
      62  : use                               | if dirname != pathname and has_magic(dirname):
      65  : RC 5->6                           | dirs = [dirname]
--------------------------------------------------------------------------------
```

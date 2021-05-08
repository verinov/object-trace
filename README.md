Trace every use of selected objects.

# Example
Running `python example.py` prints the following:
```
# Trace for label=`a`
example.py:1 (<module>)
  example.py:11 (func)
    13  : use                           | trace(a, "a")
    13  : count 2->1                    | trace(a, "a")
    15  : use                           | data["b"] = f2(a)
    example.py:7 (f2)
      7   : count 1->2                  | def f2(x):
      8   : use                         | return x
    15  : use                           | data["b"] = f2(a)
    16  : count 2->1                    | a = 11
    17  : count 1->0                    | data["b"] = f2(3)
--------------------------------------------------------------------------------
# Trace for label=`3`
example.py:1 (<module>)
  example.py:11 (func)
    14  : use                           | data["a"] = trace(3, "3")
    14  : count 30->29                  | data["a"] = trace(3, "3")
    15  : count 29->30                  | data["b"] = f2(a)
    17  : use                           | data["b"] = f2(3)
    example.py:7 (f2)
      8   : use                         | return x
    17  : use                           | data["b"] = f2(3)
    17  : count 30->29                  | data["b"] = f2(3)
    18  : use                           | data["a"] = trace(3, "3")
    18  : use                           | data["a"] = trace(3, "3")
    19  : count 30->29                  | 2 + 4
    20  : use                           | str(3) + str(3 + 1)
    22  : use                           | data["c"] = data["a"]
--------------------------------------------------------------------------------
# Trace for label=`3`
example.py:1 (<module>)
  example.py:11 (func)
    18  : use                           | data["a"] = trace(3, "3")
    19  : count 30->29                  | 2 + 4
    20  : use                           | str(3) + str(3 + 1)
    22  : use                           | data["c"] = data["a"]
--------------------------------------------------------------------------------
```

"""
`Frame` class is based on:
https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a

crusaderky commented on Feb 19:
"Happy to release this code under the Apache 2.0 license"
"""
import sys
from ctypes import POINTER, py_object, Structure, c_ssize_t, c_void_p, cast
from typing import Optional


class Frame(Structure):
    _fields_ = (
        *(
            [
                ("_ob_next", POINTER(py_object)),
                ("_ob_prev", POINTER(py_object)),
            ]
            if sys.flags.debug
            else []
        ),
        ("ob_refcnt", c_ssize_t),
        ("ob_type", c_void_p),
        ("ob_size", c_ssize_t),
        ("f_back", c_void_p),
        ("f_code", c_void_p),
        ("f_builtins", POINTER(py_object)),
        ("f_globals", POINTER(py_object)),
        ("f_locals", POINTER(py_object)),
        ("f_valuestack", POINTER(py_object)),
        ("f_stacktop", POINTER(py_object)),
    )


def get_stack_top_id(frame) -> Optional[int]:
    c_frame = Frame.from_address(id(frame))
    stack_start_addr = cast(c_frame.f_valuestack, c_void_p).value
    stack_top_addr = cast(c_frame.f_stacktop, c_void_p).value

    if stack_top_addr == stack_start_addr:
        return None

    try:
        return id(c_frame.f_stacktop[-1])
    except ValueError:
        # Sometime it raises `ValueError: PyObject is NULL`
        return None

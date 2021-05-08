"""
Everything, except for `get_stack_top_id` comes from:
https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a

crusaderky commented on Feb 19:
"Happy to release this code under the Apache 2.0 license"
"""
import sys
from ctypes import POINTER, py_object, Structure, c_ssize_t, c_void_p, sizeof
from typing import Any, Iterator, Optional, Sequence, Union


class Frame(Structure):
    _fields_ = (
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


if sys.flags.debug:
    Frame._fields_ = (
        ("_ob_next", POINTER(py_object)),
        ("_ob_prev", POINTER(py_object)),
    ) + Frame._fields_

PTR_SIZE = sizeof(POINTER(py_object))
F_VALUESTACK_OFFSET = sizeof(Frame) - 2 * PTR_SIZE
F_STACKTOP_OFFSET = sizeof(Frame) - PTR_SIZE


def get_stack_top_id(frame):
    c_frame = Frame.from_address(id(frame))
    stack_start_addr = c_ssize_t.from_address(id(frame) + F_VALUESTACK_OFFSET).value
    stack_top_addr = c_ssize_t.from_address(id(frame) + F_STACKTOP_OFFSET).value
    if stack_top_addr == stack_start_addr:
        return None
    else:
        return id(c_frame.f_stacktop[-1])

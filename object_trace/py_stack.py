import sys
from ctypes import POINTER, py_object, Structure, c_ssize_t, c_void_p, cast, c_int
from typing import Optional

assert sys.version_info.major == 3, sys.version_info

_PyObject_HEAD_EXTRA = (
    [
        ("_ob_next", py_object),
        ("_ob_prev", py_object),
    ]
    if sys.flags.debug
    else []
)


class PyObject(Structure):
    _fields_ = (
        *_PyObject_HEAD_EXTRA,
        ("ob_refcnt", c_ssize_t),
        ("ob_type", c_void_p),
    )


class PyVarObject(Structure):
    _fields_ = (
        ("ob_base", PyObject),
        ("ob_size", c_ssize_t),
    )


if 6 <= sys.version_info.minor <= 9:

    class Frame(Structure):
        _fields_ = (
            ("ob_base", PyVarObject),
            ("f_back", c_void_p),
            ("f_code", c_void_p),
            ("f_builtins", py_object),
            ("f_globals", py_object),
            ("f_locals", py_object),
            ("f_valuestack", POINTER(py_object)),
            ("f_stacktop", POINTER(py_object)),
            # the later fields are omitted
        )

    def get_stack_top_id(frame) -> Optional[int]:
        c_frame = Frame.from_address(id(frame))
        stack_start_addr = cast(c_frame.f_valuestack, c_void_p).value
        stack_top_addr = cast(c_frame.f_stacktop, c_void_p).value

        if stack_start_addr == stack_top_addr:
            return None  # empty stack

        try:
            return id(c_frame.f_stacktop[-1])
        except ValueError:
            # Sometimes it raises `ValueError: PyObject is NULL`
            return None


elif sys.version_info.minor == 10:

    class Frame(Structure):
        _fields_ = (
            ("ob_base", PyVarObject),
            ("f_back", c_void_p),
            ("f_code", c_void_p),
            ("f_builtins", py_object),
            ("f_globals", py_object),
            ("f_locals", py_object),
            ("f_valuestack", POINTER(py_object)),
            ("f_trace", py_object),
            ("f_stackdepth", c_int),
            # the later fields are omitted
        )

    def get_stack_top_id(frame) -> Optional[int]:
        c_frame = Frame.from_address(id(frame))

        if c_frame.f_stackdepth == 0:
            return None  # empty stack

        try:
            return id(c_frame.f_valuestack[c_frame.f_stackdepth - 1])
        except ValueError:
            # Sometimes it raises `ValueError: PyObject is NULL`
            return None


else:
    raise NotImplementedError(sys.version_info)

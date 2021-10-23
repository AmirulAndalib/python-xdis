# (C) Copyright 2021 by Rocky Bernstein
"""
PYPY 3.8 opcodes

This is a like Python 3.8's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    format_CALL_FUNCTION_pos_name_encoded,
    def_op,
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    update_pj3,
    varargs_op,
)

version = 3.8
version_tuple = (3, 8)
python_implementation = "PyPy"

from xdis.opcodes.opcode_33 import extended_format_MAKE_FUNCTION
import xdis.opcodes.opcode_38 as opcode_38
from xdis.opcodes.opcode_37 import format_MAKE_FUNCTION_flags

l = locals()
init_opdata(l, opcode_38, version_tuple, is_pypy=True)


# fmt: off
rm_op(l, "ROT_FOUR",    6)
rm_op(l, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(l, "LOAD_METHOD", 160)

# PyPy only
# ----------

name_op(l, "LOOKUP_METHOD",              201, 1, 2)
l["hasvargs"].append(202)
nargs_op(l, "CALL_METHOD_KW",            204, -1, 1)

# Used only in single-mode compilation list-comprehension generators
jrel_op(l, 'SETUP_EXCEPT',               121,  0,  6, conditional=True)  # ""
varargs_op(l, "BUILD_LIST_FROM_ARG",     203)
def_op(l, "LOAD_REVDB_VAR",              205)


opcode_arg_fmt = {
    "EXTENDED_ARG":  format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_flags,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
    'CALL_FUNCTION': format_CALL_FUNCTION_pos_name_encoded,
}

opcode_extended_fmt = {
    "LOAD_ATTR":     extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE":  extended_format_RETURN_VALUE,
    "STORE_ATTR":    extended_format_ATTR,
}
# fmt: on

update_pj3(globals(), l)
finalize_opcodes(l)

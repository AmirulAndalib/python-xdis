"""
For a given source or bytecode file or code object, retrieve
  * linenumbers,
  * bytecode offsets, and
  * nested functions (code objects)

This is useful for example in debuggers that want to set breakpoints only
at valid locations.
"""

from xdis.load import check_object_path,load_module
from xdis.codetype import iscode
from xdis.bytecode import get_instructions_bytes
from xdis.op_imports import get_opcode_module

from xdis.namedtuple24 import namedtuple

# Information about a single line in a particular piece of code
#  Note that a code can have several lines with the same value but
# different code.

# For example:
#     x = 1; y = 2

# will have two lines with the same line number each of the two statements.
# We will have a LineInCode object for each
LineOffsets = namedtuple("LineOffsets", ["line_number", "offsets", "code"])
LineOffsetsCompact = namedtuple("LineOffsetsCompact", ["name", "offsets"])


class LineOffsetInfo(object):
    def __init__(self, opc, code, include_children=False):
        if not iscode(code):
            raise TypeError(
                "code parameter %s needs to be a code type; is %s" % (code, type(code))
            )

        self.code = code
        self.name = code.co_name
        self.opc = opc
        self.children = {}
        self.lines = []
        self.offsets = []
        self.linestarts = dict(opc.findlinestarts(code, dup_lines=True))
        self.instructions = []
        last_line_info = None
        for instr in get_instructions_bytes(
            bytecode=code.co_code,
            opc=opc,
            varnames=code.co_varnames,
            names=code.co_names,
            constants=code.co_consts,
            cells=code.co_cellvars + code.co_freevars,
            linestarts=self.linestarts,
        ):
            offset = instr.offset
            self.offsets.append(offset)
            self.instructions.append(instr)
            if instr.starts_line:
                if last_line_info:
                    self.lines.append(last_line_info)
                    pass
                last_line_info = LineOffsets(instr.starts_line, [offset], code)
            else:
                last_line_info.offsets.append(offset)
                pass
            pass
        if include_children:
            for c in code.co_consts:
                if iscode(c):
                    code_info = LineOffsetInfo(opc, c, True)
                    self.children[code_info.name] = code_info
                    pass
                pass
            pass
        self.lines.append(last_line_info)
        return

    def __str__(self):
        return str(self.line_numbers())

    def line_numbers(
        self, include_children=False, include_dups=True, include_offsets=False
    ):
        """Return all of the valid lines for a given piece of code"""
        if include_offsets:
            lines = {}
            for li in self.lines:
                lines[li.line_number] = LineOffsetsCompact(
                    li.code.co_name, li.offsets
                )
                pass
            pass
        else:
            lines = list(self.linestarts.values())
        if include_children:
            for child in self.children.values():
                child_lines = child.line_numbers(
                    include_children=True,
                    include_dups=include_dups,
                    include_offsets=include_offsets,
                )
                if include_offsets:
                    lines.update(child_lines)
                else:
                    lines.append(child_lines)
                pass
        return lines

    pass


def lineoffsets_in_file(filename, toplevel_only=False):
    obj_path = check_object_path(filename)
    version, timestamp, magic_int, code, pypy, source_size, sip_hash = load_module(
        obj_path
    )
    if pypy:
        variant = "pypy"
    else:
        variant = None
    opc = get_opcode_module(version, variant)
    return LineOffsetInfo(opc, code, not toplevel_only)
    pass


def lineoffsets_in_module(module, toplevel_only=False):
    return lineoffsets_in_file(module.__file__, toplevel_only)


if __name__ == "__main__":

    def foo():
        def bar():
            return 5

        x = 1
        y = 2
        a = 3
        b = 4
        return x, y, a, b

    def print_code_info(code_info):
        children = code_info.children.keys()
        if len(children):
            print("%s has %d children" % (code_info.name, len(children)))
            for child in code_info.children.keys():
                print("\t%s" % child)
                pass
            print("\n")
        else:
            print("%s has no children" % (code_info.name))

        print("\tlines with dups %s" % code_info.line_numbers(include_dups=True))
        print("\tlines without dups %s" % code_info.line_numbers(include_dups=False))
        print(
            "\tlines without dups and children %s"
            % code_info.line_numbers(include_children=True, include_dups=False)
        )
        print("Offsets in %s" % code_info.name, code_info.offsets)
        lines = code_info.line_numbers(include_offsets=True, include_children=True)
        for line_num, li in lines.items():
            print("\tname: %s, line %4d, offsets %s" % (li.name, line_num, li.offsets))
        print("=" * 30)
        for li in code_info.lines:
            print(li)
            pass
        return

    print_code_info(lineoffsets_in_file(__file__))

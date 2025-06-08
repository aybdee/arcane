from pprint import pprint
from sys import argv
from typing import Tuple

from lark import Transformer

from arcane.core.models.constructs import Program
from arcane.core.parsing.parser import parse
from arcane.core.parsing.process import resolve_dependencies
from arcane.core.parsing.transfomer import ArcaneTransfomer
from arcane.core.runtime.interpreter import ArcaneInterpreter

if len(argv) < 2:
    print("error: arc file not supplied")
else:
    if argv[1].endswith(".arc"):
        with open(argv[1], "r") as f:
            tree = parse(f.read())
            program = ArcaneTransfomer().transform(tree)
            program = resolve_dependencies(program)
            interpreter = ArcaneInterpreter(program)
            interpreter.run()
    else:
        print("error: file is not an arc file")

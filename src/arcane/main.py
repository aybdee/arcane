from lark import Transformer
from sys import argv
from arcane.core.constructs import Program
from arcane.core.interpreter import ArcaneInterpreter, InterpreterMessage
from arcane.core.parser import parse
from arcane.core.transfomer import ArcaneTransfomer
from pprint import pprint

if len(argv) < 2:
    print("error: arc file not supplied")
else:
    if argv[1].endswith(".arc"):
        with open(argv[1], "r") as f:
            tree = parse(f.read())
            program = ArcaneTransfomer().transform(tree)
            interpreter = ArcaneInterpreter(program)
            interpreter.run()

    else:
        print("error: file is not an arc file")

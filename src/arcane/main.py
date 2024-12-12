from lark import Transformer
from arcane.core.constructs import Program
from arcane.core.interpreter import ArcaneInterpreter, InterpreterMessage
from arcane.core.parser import parse
from arcane.core.transfomer import ArcaneTransfomer
from pprint import pprint


with open("../test/define.arc","r") as f:
    tree = parse(f.read())
    program = ArcaneTransfomer().transform(tree)
    interpreter = ArcaneInterpreter(program)
    interpreter.run()

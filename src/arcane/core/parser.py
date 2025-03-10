from lark import Lark, ParseTree
import os
from arcane.utils import get_project_root

grammar = ""
with open(os.path.join(get_project_root(), "src/arcane/grammar/arcane.lark"), "r") as f:
    grammar = f.read()

parser = Lark(grammar)


def parse(source: str) -> ParseTree:
    tree = parser.parse(source)
    return tree

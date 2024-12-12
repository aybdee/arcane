from lark import Transformer
from sympy import sympify

from arcane.core.constructs import Animation, Definition, Identifier, InstanceAnimation, MathFunction, ArcaneType, MultiSweepTransform, Program, SweepTransform, Transform

class ArcaneTransfomer(Transformer):
    def program(self,items):
        statements = []
        for item in items:
            statements.append(item)
        return Program(statements)

    def definition(self,items):
        name = None
        value = None
        arctype = None
        transform = None
        for item in items:
            if isinstance(item,Identifier):
                name = item
            elif isinstance(item,MathFunction):
                arctype = ArcaneType.MATHFUNCTION
                value = item

            elif isinstance(item,Transform):
                transform = item
                
        assert name is not None
        assert value is not None
        assert arctype is not None
        return Definition(arctype,name,value,transform)

    def animate_declaration(self,items):
        items = list(filter(lambda x: x!=None,items))
        if len(items) == 1:
            return Animation(value=items[0])
        else:
            return Animation(value=InstanceAnimation(instance=items[0],transform=items[1]))
            
    
    def math_function(self,items):
        variables = []
        expression = ""
        for item in items:
            if isinstance(item,Identifier):
                variables.append(item)
            else:
                expression = item
        return MathFunction(variables, expression)


    def sweep(self,items):
        return SweepTransform(items[0],items[1])

    def multi_sweep(self,items):
        current_identifier = None
        transforms = []
        for item in items:
            if isinstance(item,SweepTransform):
                transforms.append((current_identifier,item))
            else:
                current_identifier = item
        return MultiSweepTransform(transforms)

    def numerical_expression(self,items):
        return sympify(" ".join(items))
    
    def numerical_factor(self,items):
        return " ".join(items)
    
    def numerical_term(self,items):
        return " ".join(items)

    def numerical_base(self,items):
        repr_string = ""
        for item in items:
            if isinstance(item,Identifier):
                repr_string += f"{item.value}"
            else:
                repr_string  += f"{item}"
        return repr_string

    def algebraic_expression(self,items):
        return sympify(" ".join(items))
    
    def algebraic_factor(self,items):
        return " ".join(items)
    
    def algebraic_term(self,items):
        return " ".join(items)

    def algebraic_base(self,items):
        repr_string = ""
        for item in items:
            if isinstance(item,Identifier):
                repr_string += f"{item.value}"
            else:
                repr_string  += f"{item}"
        return repr_string

    
    def NUMBER(self, n):
        return float(n)
    
    def IDENT(self,n):
        return Identifier(str(n))
    
    def MUL(self,_):
        return "*"

    def DIV(self,_):
        return "/"
    
    def ADD(self,_):
        return "+"

    def SUB(self,_):
        return "-"

    def MOD(self,_):
        return "%"

    def EXP(self,_):
        return "^"

    #process non terminal nodes
    def expression(self,items):
        return items[0]

    def statement(self,items):
        return items[0]

    def start(self,items):
        return items[0]
    
    def math_transform(self,items):
        return items[0]

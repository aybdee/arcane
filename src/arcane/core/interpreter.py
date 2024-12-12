from dataclasses import dataclass
from arcane.core.constructs import Animation, Definition, InstanceAnimation, MathFunction, Program
from enum import Enum

from arcane.graphics.constructor import animate_math_function
from arcane.graphics.scene import construct_scene


class InterpreterError(Enum):
    NO_STATEMENTS_AVAILABLE = ("No statements left to evaluate", None)
    UNDEFINED_VARIABLE = ("Undefined variable", None)
    
    def __new__(cls, label, data):
        obj = object.__new__(cls)
        obj._value_ = label
        obj.data = data
        return obj

    def with_data(self, data):
        self.data = data
        return self

class InterpreterMessage(Enum):
    SUCCESS = ("statement evaulated", None)
    
    def __new__(cls, label, data):
        obj = object.__new__(cls)
        obj._value_ = label
        obj.data = data
        return obj

    def with_data(self, data):
        self.data = data
        return self

    

class Store():
    def __init__(self):
        self.store = {}

    def add(self,key,value):
        self.store.update({key:value})
        
    def get(self,key):
        return self.get(key)
    
    def __str__(self):
        return str(list(self.store.keys()))

class ArcaneInterpreter():
    def __init__(self,program:Program):
        self.program = program
        self.store = Store()
        self.instruction_pointer = 0
    
    def execute_next(self) -> InterpreterMessage | InterpreterError:
        if len(self.program.statements) - 1  < self.instruction_pointer:
            return InterpreterError.NO_STATEMENTS_AVAILABLE

        current_statement = self.program.statements[self.instruction_pointer]
        self.instruction_pointer += 1
        if isinstance(current_statement,Definition):
            return self.handle_definition(current_statement)

        elif isinstance(current_statement,Animation):
            return self.handle_animation(current_statement)
        return InterpreterMessage.SUCCESS
   
    def handle_definition(self,definition:Definition):
        self.store.add(definition.name.value,definition.value)
        return InterpreterMessage.SUCCESS

    
    def handle_animation(self,animation:Animation):
        if isinstance(animation.value,InstanceAnimation):
            if isinstance(animation.value.instance,MathFunction):
                return InterpreterMessage.SUCCESS.with_data(animate_math_function(animation.value.instance,animation.value.transform))
            else:
                value = self.store.get(animation.value.instance.value)
                if value:
                    return self.handle_animation(value)
                else:
                    return InterpreterError.UNDEFINED_VARIABLE.with_data(animation.value.instance.value)
        return InterpreterMessage.SUCCESS

    def run(self):
        animation_blocks = []
        for i in range(len(self.program.statements)):
            result = self.execute_next()
            if isinstance(result,InterpreterMessage):
                if result.data:
                    animation_blocks.append(result.data)
        
        arcane_animation = construct_scene(animation_blocks)()
        arcane_animation.render()

    
    def __str__(self):
        return f"""
        instruction_pointer: {self.instruction_pointer}
        variables: {str(self.store)}
        """

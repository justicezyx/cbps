import re

INT = 'INT'
DOUBLE = 'DOU'
CHAR = 'CHR'

IN = 'in'
LT = '<'
GT = '>'
LE = '<='
GE = '>='


class Subscription:
    def __init__(self, data):
        self.attrConstraints = {}

        for constraint in data.split('}{')
            constraint = constraint.strip('{}')
            Type,Name,Op,Val = constraint.split(':', 3)
            
            self.attrConstraints[Name] = Constraint(Type, Op, Val)

        self.count = len(self.attrConstraints)

            
    def Match(self, **val):
        if len(val) < self.count:
            return False

        for name,constraint in self.attrConstraints.items():
            if not val.has_key(name): # has no value for the attr
                return False

            if not constraint.Match(val[name]):
                return False

        return True

class Constraint:
    def __init__(self, tp, op, val):
        
    

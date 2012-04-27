import re

INT = 'INTEGER'
DOU = 'DOUBLE'
STR = 'STRING'

IN = 'in'
LT = '<'
GT = '>'
LE = '<='
GE = '>='


class Subscription:
    def __init__(self, data):
        self.attrConstraints = {}

        for constraint in data.split('}{'):
            constraint = constraint.strip('{}')
            Type,Name,Op,Val = constraint.split(',', 3)
            
            self.attrConstraints[Name] = Constraint(Type, Op, Val)

        self.count = len(self.attrConstraints)

    # val argument is assumed to be a comma-separated string
    # no white space is allowed. each field, which is separated by a comma,
    # is an attribute assignment of the form "attribute name"="type:value"
    def Match(self, val):
        vals = val.split(",")
        if len(vals) < self.count:
            return False

        assignments = {}
        for v in vals:
            name,assignment = v.split("=")
            
            assignmentType, assignmentString = assignment.split(":")
            val = CreateType(assignmentType).Parse(assignmentString)
            assignments[name] = val
            
        for name,constraint in self.attrConstraints.items():
            if not assignments.has_key(name):
                return False
            if not constraint.Match(assignments[name]):
                return False

        return True
            
    #def Match(self, **val):
        #if len(val) < self.count:
            #return False

        #for name,constraint in self.attrConstraints.items():
            #if not val.has_key(name): # has no value for the attr
                #return False

            #if not constraint.Match(val[name]):
                #return False

        #return True

class OpIN:
    def Check(self, cons, val):
        return val > cons[0] and val < cons[1]

class OpGT:
    def Check(self, cons, val):
        return val > cons

class OpGE:
    def Check(self, cons, val):
        return val >= cons

class OpLT:
    def Check(self, cons, val):
        return val < cons

class OpLE:
    def Check(self, cons, val):
        return val <= cons

def CreateOperator(type):
    if type == IN:
        return OpIN()

    if type == GT:
        return OpGT()
    
    if type == GE:
        return OpGE()

    if type == LT:
        return OpLT()

    if type == LE:
        return OpLE()

class TypeInteger:
    def Parse(self, val):
        return int(val)

class TypeDouble:
    def Parse(self, val):
        return float(val)

class TypeString:
    def Parse(self, val):
        return val

def CreateType(tp):
    if tp == INT:
        return TypeInteger()

    if tp == DOU:
        return TypeDouble()

    if tp == STR:
        return TypeString()
    
class Constraint:
    def __init__(self, tp, op, val):
        self.type = CreateType(tp)
        self.optr = CreateOperator(op)
        self.value = val

    def Match(self, val):
        v = self.type.Parse(val)
        return self.optr.Check(self.value, v)
        
if __name__ == '__main__':
    sub = Subscription('{INTEGER,age,<,100}{INTEGER,height,<=,200}')
    if sub.Match("age=INTEGER:10,height=INTEGER:10"):
        print "correct"

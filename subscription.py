"""
Attribute value types
"""

INT = 'INTEGER'
DOU = 'DOUBLE'
STR = 'STRING'

"""
Operators
"""

IN = 'in'
LT = '<'
GT = '>'
LE = '<='
GE = '>='
EQ = '='

def FormatCheck(string):
    """
    Subscription format check
    """

    for c in string.split('}{'):
        cons = c.split(',')
        if len(cons) < 4 or len(cons) > 5:
            return False
        
        for con in cons:
            if len(con) == 0:
                return False
    return True

def ParseAttributeAssignments(string):
    """
    Attribute assignments have format as follows:
    [[attribute name]=[attribute type]:[value]],[other attribute assignment]
    """

    vals = string.split(',')
    res = {}
    for v in vals:
        name,value = v.split("=")
        valueType, valueString = value.split(":")
        val = CreateType(valueType).Parse(valueString)
        res[name] = val
    return res

class Subscription:
    """
    Subcription will have the format as follows:
    {[attribute value type],[attribute name],[operator],[value]}{[other constraints]}
    """

    def __init__(self, data):
        self.attrConstraints = {}
        for constraint in data.split('}{'):
            constraint = constraint.strip('{}')
            Type,Name,Op,Val = constraint.split(',', 3)
            self.attrConstraints[Name] = Constraint(Type, Op, Val)
        self.count = len(self.attrConstraints)

    def Match(self, assignments):
        """
        Attribute assignments have format as follows:
        [attribute name]=[attribute type]:[value],[other attribute assignment]
        """

        for name,constraint in self.attrConstraints.items():
            if not assignments.has_key(name):
                return False
            if not constraint.Match(assignments[name]):
                return False

        return True
            
class OpIN:
    def Check(self, cons, val):
        return val > cons[0] and val < cons[1]

class OpEQ:
    def Check(self, cons, val):
        return val == cons

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

    if type == EQ:
        return OpEQ()

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
        self.optr = CreateOperator(op)
        if op == IN:
            vals = val.split(',')
            self.value = (CreateType(tp).Parse(vals[0]), CreateType(tp).Parse(vals[1]))
        else:
            self.value = CreateType(tp).Parse(val)

    def Match(self, val):
        return self.optr.Check(self.value, val)
        
if __name__ == '__main__':
    sub = Subscription('{INTEGER,age,>,1}')
    if sub.Match(ParseAttributeAssignments("age=INTEGER:2,height=INTEGER:2")):
        print "correct"

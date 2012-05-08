""" Attribute value types
Constaints that represent value types
"""
INT = 'INTEGER'
DOU = 'DOUBLE'
STR = 'STRING'

""" Operators
Constaints that represent operators
"""
IN = 'in'
LT = '<'
GT = '>'
LE = '<='
GE = '>='
EQ = '='

class AttributeAssignment:
    def __init__(self, string):
        self.rep = string

        vals = string.split(',')
        self.values = {}
        for v in vals:
            name,value = v.split('=')
            valueType, valueString = value.split(':')
            val = CreateType(valueType).Parse(valueString)
            self.values[name] = val

    def __getitem__(self, name):
        return self.values[name]

    def __repr__(self):
        return self.rep

    def has_key(self, name):
        return self.values.has_key(name)

class Subscription:
    """ Subcription will have the format as follows:

    {[attribute value type],[attribute name],[operator],[value]}{[other constraints]}
    """

    def __init__(self, data):
        self.rep = data

        self.attrConstraints = {}
        for constraint in data.split('}{'):
            constraint = constraint.strip('{}')
            #Type,Name,Op,Val = constraint.split(',', 3)
            #self.attrConstraints[Name] = AttributeConstraint(Type, Op, Val)

            ac = AttributeConstraint(constraint)
            self.attrConstraints[ac.attrName] = ac

        self.count = len(self.attrConstraints)

    def __repr__(self):
        return self.rep
        

    def Match(self, assignments):
        """ Attribute assignments have format as follows:

        [attribute name]=[attribute type]:[value],[other attribute assignment]
        A AttributeAssignment object will handle this format
        """

        for name,constraint in self.attrConstraints.items():
            if not assignments.has_key(name):
                return False
            if not constraint.Match(assignments[name]):
                return False

        return True

    @staticmethod
    def FormatCheck(string):
        """ Subscription format check

        Subscriptions have the format as follows:
        {[attribute value type],
         [attribute name],
         [operator],
         [attribute value]}{other attribute constrants}
        
        No white space is allowed
        The sender of a subscription should strips all leading and trailing white spaces
        """

        MIN_FIELD_NUM = 4
        MAX_FIELD_NUM = 5

        for c in string.split('}{'):
            cons = c.split(',')
            if len(cons) < MIN_FIELD_NUM or len(cons) > MAX_FIELD_NUM:
                return False
            
            for con in cons:
                if len(con) == 0:
                    return False
        return True


# operators
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
            
class OpIN:
    def Check(self, cons, val):
        return val > cons[0] and val < cons[1]

    def __repr__(self):
        return IN

class OpEQ:
    def Check(self, cons, val):
        return val == cons

    def __repr__(self):
        return EQ

class OpGT:
    def Check(self, cons, val):
        return val > cons

    def __repr__(self):
        return GT

class OpGE:
    def Check(self, cons, val):
        return val >= cons

    def __repr__(self):
        return GE

class OpLT:
    def Check(self, cons, val):
        return val < cons

    def __repr__(self):
        return LT

class OpLE:
    def Check(self, cons, val):
        return val <= cons

    def __repr__(self):
        return LE

# Attribute value types
def CreateType(tp):
    if tp == INT:
        return TypeInteger()

    if tp == DOU:
        return TypeDouble()

    if tp == STR:
        return TypeString()

class TypeInteger:
    def Parse(self, val):
        return int(val)

    def __repr__(self):
        return INTEGER

class TypeDouble:
    def Parse(self, val):
        return float(val)

    def __repr__(self):
        return DOUBLE

class TypeString:
    def Parse(self, val):
        return val
    
    def __repr__(self):
        return STRING

class AttributeConstraint:
    """ AttributeConstraint

    A 4-tuple with type, name, op, value
    """

    #def __init__(self, tp, op, val):
    def __init__(self, *rep):
        if len(rep) > 1:
            tp, name, op, val = rep
            self.rep = ','.join(rep)
        else:
            tp, name, op, val = rep[0].split(',', 3)
            self.rep = rep[0]
            
        self.attrName = name
        self.optr = CreateOperator(op)
        if op == IN:
            vals = val.split(',')
            self.value = (CreateType(tp).Parse(vals[0]), CreateType(tp).Parse(vals[1]))
        else:
            self.value = CreateType(tp).Parse(val)

    def __repr__(self):
        return self.rep

    def Match(self, val):
        return self.optr.Check(self.value, val)
        
if __name__ == '__main__':
    sub = Subscription('{INTEGER,age,=,2}{INTEGER,height,>,1}')
    aa = AttributeAssignment("age=INTEGER:2,height=INTEGER:2")
    if sub.Match(aa):
        print 'correct'

    print str(aa)
    print str(sub)

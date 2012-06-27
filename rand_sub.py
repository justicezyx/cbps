import random
import sys

if len(sys.argv) >= 2:
    num = int(sys.argv[1])
else:
    num = 100

for i in xrange(num):
    l = random.randint(1, 100)
    r = random.randint(1, 100)

    if l > r:
        l, r = r, l

    subtext = 'SUB,{INTEGER,age,in,' + str(l) + ',' + str(r) + '}'

    print subtext

import uuid
import time
import datetime
a1 = -10
a2 = 5.4
a3 = 3.334
a4 = "10.2"

float(a1)
d = {"a1": 10, "a2": 5, "a3":3}
s = "#3 + #2 * 2 + (#1 * 2) / 2"
for i in range(1,4):
    s = s.replace(f"#{i}", str(d.get(f'a{i}')))
print(s)
value = eval(s)
print(value)

import re
s2 = "{专制} + {独裁} + {D}"
par = re.compile(r'{.*?}', )
res = par.findall(s2)
print(res)
exp = "3>1 and 4>2 or 4>2"
print(exp)
print(1)

s = "我们我们我们我们我们我们我们我们我们"
print(len(s))

l = "\\"
print("\\" == l)
print('\\' == "\\\\")
ss = uuid.uuid4()
print(ss)







import uuid

a1 = 10
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

print(1 != 2)
[{"value": "c4bde9fa-4b54-477d-92b9-6cb38da57d84", "label": "#1", "type": "question_id"}, {"value": "+", "label": "+", "type": "symbol"}, {"value": "d2f39c72-f90a-4578-8ee5-3718fdb6d1ab", "label": "#2", "type": "question_id"}, {"value": "+", "label": "+", "type": "symbol"}, {"value": "d5afc592-1c3d-4369-8545-ae68f0c68aa2", "label": "#3", "type": "question_id"}, {"value": "+", "label": "+", "type": "symbol"}, {"value": "f97ae39a-6204-4188-8ecd-cc7375c38abd", "label": "#4", "type": "question_id"}, {"value": "+", "label": "+", "type": "symbol"}, {"value": "da781306-f439-4848-82e9-5d2268a9d20b", "label": "#5", "type": "question_id"}]
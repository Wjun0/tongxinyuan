a1 = 10
a2 = 5
a3 = 3

d = {"a1": 10, "a2": 5, "a3":3}
s = "#3 + #2 * 2 + (#1 * 2) / 2"
for i in range(1,4):
    s = s.replace(f"#{i}", str(d.get(f'a{i}')))
print(s)
value = eval(s)
print(value)


s2 = "{专制} + {独裁} + {D}"

exp = 3>1 and 4>2 or 4>2
print(exp)
print(1)

s = "我们我们我们我们我们我们我们我们我们"
print(len(s))

l = "\\"
print("\\" == l)
print('\\' == "\\\\")
from django.test import TestCase

# Create your tests here.

import re

n = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search("name")
m = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search("na你哈me")
o = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search("name你113")
p = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search("你好12name你")
pp = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search("你好$name你")
if p:
    print(p)
if pp:
    print(pp)
print(n)
print(m)
print(o)
print(p)
print(pp)
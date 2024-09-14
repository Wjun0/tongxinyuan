from django.test import TestCase

# Create your tests here.
print(len("儿童行为量表（CBCL）Achenbach".encode('utf-8')))
print(len("儿童行为量表".encode('utf-8')))
print(len("（".encode('utf-8')))
print(len("Ac".encode('utf-8')))
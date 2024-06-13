from django.test import TestCase

# Create your tests here.
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tong-psy.settings')
import re, uuid
from django.utils import timezone
from utils.generate_jwt import generate_jwt, jwt_decode

token = generate_jwt({"user_id": "12345"}, 1)
jwt_decode(token)
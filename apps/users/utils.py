from apps.users.models import User
from utils.generate_jwt import jwt_decode

def token_to_name(token):
    data = jwt_decode(token)
    user_id = data.get('data',{}).get('user_id')
    obj = User.objects.filter(user_id=user_id).first()
    return obj.name

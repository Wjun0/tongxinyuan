import os
import uuid
from django.conf import settings
from apps.questions.models import Image
from apps.users.exceptions import Exception_


def upload(request):
    file = request.data.get("file")
    data = request.data
    source = data.get('source', '')
    if source not in ["background_img", "title_img", "result_img", "content_img"]:
        raise Exception_("参数类型错误！")
    if not file:
        raise Exception_("文件不能为空！")
    file_name = file.name
    file_type = file_name.split('.')[-1]
    if file_type not in ["png", "jpg", "gif"]:
        raise Exception_("不支持该类型文件！")
    uid = str(uuid.uuid4())
    file_id = f"{uid}.{file_type}"
    Image.objects.create(file_id=file_id, file_name=file_name, source=source)
    with open(os.path.join(settings.BASE_DIR, "media", "image", file_id), 'wb')as f:
        f.write(file.read())
    return file_id, file_name


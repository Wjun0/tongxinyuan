import os
import shutil

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from apps.users.models import Document
from apps.users.permission import isManagementPermission


class IndexUploadView(CreateAPIView):
    permission_classes = (isManagementPermission, )

    def create(self, request, *args, **kwargs):
        upload_file = request.FILES.get('file')  # 获取分片
        task = request.POST.get('task_id')  # 获取文件唯一标识符
        print("分片", task)
        real_file_name = upload_file._name
        print("===========")
        print(real_file_name)
        # if names[-1] not in ["mp4", "flv", "avi", "mov", "m4a", "mp3", "wav", "ogg", "asf", "au", "voc", "aiff", "rm",
        #                      "svcd", "vcd"]:
        #     return Response({"detail": "不支持该文件类型！"}, status=400)
        chunk = request.POST.get('chunk', 0)
        print("分片上传", chunk)
        filename = './media/file/%s%s' % (task, chunk)
        if not os.path.exists(filename):
            try:
                with open(filename, 'wb') as f:
                    for obj in upload_file.chunks():
                        f.write(obj)
                    f.write(upload_file.read())
                    f.close()
                return Response({"detail": "success"})
            except Exception as e:
                return Response({"detail": "error"}, status=400)
        return Response({"detail": "path error"}, status=400)


class SuccessUploadView(CreateAPIView):
    permission_classes = (isManagementPermission, )

    def create(self, request, *args, **kwargs):
        """所有分片上传成功"""
        print("所有分片上传成功")
        task = request.POST.get('task_id')
        print("所有分片", task)
        ext = request.POST.get('ext', '')
        print('ext:', ext)
        upload_type = request.POST.get('type')
        print('upload_type:', upload_type)
        name = request.POST.get('name')
        print('name:', name)
        if len(ext) == 0 and upload_type:
            ext = upload_type.split('/')[1]
        chunk = 0
        with open("./media/file/%s" % name, 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = './media/file/%s%s' % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                    os.remove(filename)  # 删除该分片，节约空间
                except Exception as e:
                    # 找不到碎片文件跳出循环
                    break
                chunk += 1
            target_file.close()
            import uuid
            file_id = str(uuid.uuid4())
            new_name = file_id + '.' + name.split('.')[-1]
            mymovefile("./media/file/%s" % name, "./media/qrcode/%s" % new_name)
            # 把路径储存入数据库中
            Document.objects.create(docfile= file_id, filename=new_name)
            return Response({"message": "success", "file_id": file_id})

#移动文件到新文件路径
def mymovefile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(srcfile, dstfile)  # 移动文件
        print("move %s -> %s" % (srcfile, dstfile))
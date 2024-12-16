import os
import shutil
import subprocess
import time

from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from apps.users.models import Document
from apps.users.permission import isManagementPermission
import logging
LOG = logging.getLogger('log')

class IndexUploadView(CreateAPIView):
    permission_classes = (isManagementPermission, )

    def create(self, request, *args, **kwargs):
        upload_file = request.FILES.get('file')  # 获取分片
        task = request.POST.get('task_id')  # 获取文件唯一标识符
        print("分片", task)
        real_file_name = upload_file._name
        print("===========")
        print(real_file_name)
        if real_file_name.split('.')[-1] not in ["mp4", "mp3"]:
            return Response({"detail": "仅支持上传mp3和mp4格式！"}, status=400)
        chunk = request.POST.get('chunk', 0)
        print("分片上传", chunk)
        filename = './media/file/%s%s' % (task, chunk)
        if not os.path.exists(filename):
            try:
                with open(filename, 'wb') as f:
                    # for obj in upload_file.chunks():
                    #     f.write(obj)
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
        m3u8_name = file_id + '.m3u8'
        old_path = os.path.join(settings.BASE_DIR, "media", "qrcode", new_name)
        m3u8_path = os.path.join(settings.BASE_DIR, "media", "qrcode", m3u8_name)
        cmd = f'ffmpeg -i {old_path} -c copy -bsf:v h264_mp4toannexb -hls_time 5  {m3u8_path}'
        # cmd = f'D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -i {old_path} -c copy -bsf:v h264_mp4toannexb -hls_time 5  {m3u8_path}'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            cmd = f'ffmpeg -i {old_path} -c copy -bsf:v hevc_mp4toannexb -hls_time 5  {m3u8_path}'
            # cmd = f'D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -i {old_path} -c copy -bsf:v hevc_mp4toannexb -hls_time 5  {m3u8_path}'
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                LOG.error(f"{time.asctime()} fail upload file {new_name} \r {result.stderr}")
                return Response({"detail": "fail", "data": "文件上传失败！"})

        # 把路径储存入数据库中
        Document.objects.create(docfile=m3u8_name, filename=new_name)
        return Response({"message": "success", "file_id": m3u8_name})

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
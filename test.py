import time
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tong-psy.fat_settings')
import django
django.setup()
from apps.questions.models import Image
import ffmpeg
import json

def get_video_codec(file_path):
    # 定义一个函数，接收一个文件路径作为参数
    try:
        # 使用ffmpeg.probe获取视频文件的信息
        probe = ffmpeg.probe(file_path)
        # 从返回的数据中提取视频编码格式
        video_streams = probe['streams']
        for stream in video_streams:
            return stream['codec_name']
            # if stream['codec_type'] == 'video':
            #     return stream['codec_name']  # 返回编码格式
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")  # 捕获并打印错误
    return None  # 如果没有找到，返回None


def test_ffmpeg():
    import subprocess
    old_path = "C:\\Users\\18212\\Desktop\\code\\tong-psy\\111.mp4"
    m3u8_path = "C:\\Users\\18212\\Desktop\\code\\tong-psy\\13.m3u8"

    ffmpeg = "D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg"
    cmd = f'{ffmpeg} -i {old_path} -c copy -bsf:v h264_mp4toannexb -hls_time 50  {m3u8_path}'

    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('Error:', result.stderr)
    else:
        print('Output:', result.stdout)

    print('mp4转换ts命令执行完毕')

def update_m3u8():
    from pathlib import Path
    import os
    import subprocess
    base_dir = Path(__file__).resolve().parent
    path = os.path.join(base_dir, "media", "media_data")
    file_list = os.listdir(path)
    m3u8_file = []
    for i in file_list:
        try:
            uid, type = i.split('.')
            if type not in ['ts', 'm3u8']:
                if uid + '.m3u8' not in file_list:
                    m3u8_file.append(i)
        except:
            pass
    print(m3u8_file)
    for i in m3u8_file:
        uid, type = i.split('.')
        old_path = os.path.join(base_dir, "media", "media_data", i)
        m3u8_path = os.path.join(base_dir, "media", "media_data", uid +'.m3u8')

        cmd = f'ffmpeg -i {old_path} -c copy -bsf:v h264_mp4toannexb -hls_time 5  {m3u8_path}'
        # cmd = f'D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -i {old_path} -c copy -bsf:v h264_mp4toannexb -hls_time 5  {m3u8_path}'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            cmd = f'ffmpeg -i {old_path} -c copy -bsf:v hevc_mp4toannexb -hls_time 5  {m3u8_path}'
            # cmd = f'D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -i {old_path} -c copy -bsf:v hevc_mp4toannexb -hls_time 5  {m3u8_path}'

            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(result.stderr)
                print("fail")
            else:
                print('success!')
        else:
            print('success')

def update_mysql_m3u8():
    objs = Image.objects.filter(source='media_data')
    for i in objs:
        uid, type = i.file_id.split('.')
        i.m3u8 = uid + '.m3u8'
        i.save()


if __name__ == '__main__':
    s = "ssss.mp4"
    a,b = s.split('.')
    test_ffmpeg()
    # update_m3u8()  # 测试已更新
    # update_mysql_m3u8()  # 测试已更新





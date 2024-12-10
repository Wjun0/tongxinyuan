import time

def test_ffmpeg():
    mp4 = "C:\\Users\\18212\\Desktop\\code\\tong-psy\\11.mp4"
    m3u8 = "C:\\Users\\18212\\Desktop\\code\\tong-psy\\11.m3u8"

    cmd1 = "D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -version"
    cmd = f'D:\\ffmpeg-7.0.2-full_build-shared\\bin\\ffmpeg -i {mp4} -c copy -bsf:v h264_mp4toannexb -hls_time 5  {m3u8}'
    import subprocess
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
        type = 'h264_mp4toannexb'

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



if __name__ == '__main__':
    # test_ffmpeg()
    update_m3u8()






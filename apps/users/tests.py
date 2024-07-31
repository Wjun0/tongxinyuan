import os
import sys
from pathlib import Path




def update_table():
    from apps.users.models import Media
    meds = Media.objects.filter(file_id="")
    for i in meds:
        if not i.path:
            i.file_id = i.id
        i.file_id = i.path.split('.')[0]
        i.save()


def test_re():
    import re
    user_name = "1我"
    s = re.compile(r'^[\u4e00-\u9fff]+$').search(user_name)
    print(s)

if __name__ == '__main__':
    #test_re()
    from datetime import datetime

    now = datetime.now()

    # 时间戳（纳秒级别）
    timestamp_nanoseconds = now.timestamp() * 10 ** 9

    print(timestamp_nanoseconds)
    import random, string
    name = ""
    now = datetime.now()
    name = name if name else f"{now.strftime('%Y%m%d%H%M%S')}{random.randint(1111,9999)}{''.join(random.choices(string.ascii_lowercase, k=2))}"
    print(name)
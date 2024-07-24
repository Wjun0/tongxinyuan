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
    pwd = "233nfdslj&@#$"
    s = re.search(r'[\u4e00-\u9fff]', pwd)
    print(s)

if __name__ == '__main__':
    test_re()
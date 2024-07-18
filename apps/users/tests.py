import os
import sys
from pathlib import Path



from apps.users.models import Media

def update_table():
    meds = Media.objects.filter(file_id="")
    for i in meds:
        if not i.path:
            i.file_id = i.id
        i.file_id = i.path.split('.')[0]
        i.save()

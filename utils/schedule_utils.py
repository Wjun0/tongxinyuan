from apps.users.models import User
from django.utils import timezone

def update_user_status():
    users = User.objects.filter(tag=0, status__in=["used", "pending"])
    for i in users:
        now = timezone.now()
        if i.status == "used":  # 生效中的
            if i.start_time < now < i.end_time:
                pass
            else:
                i.status = "deleted"
                i.save()
        else:
            if i.start_time < now < i.end_time:
                i.status = "used"
                i.save()
            elif i.start_time < now and i.end_time < now:
                i.status = "deleted"
                i.save()

    return
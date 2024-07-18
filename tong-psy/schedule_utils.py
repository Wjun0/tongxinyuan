from apps.users.models import User


def update_user_status():
    users = User.objects.filter(tag=0, status__in=["used", "pending"])
    for i in users:
        if i.status == "used":  # 生效中的
            pass
        else:
            pass
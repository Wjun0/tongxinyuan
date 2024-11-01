from django.db.models import Q

from apps.questions.models import QuestionType
from apps.users.models import User
from apps.users.utils import get_user_id
from apps.wechats.services import user_is_payed


def filter_queryset(queryset, request):
   data = request.query_params
   phone = data.get("phone")
   user_name = data.get("user_name")
   start_time = data.get("start_time")
   end_time = data.get("end_time")
   title = data.get("title")
   # user_id = get_user_id(request.META.get('HTTP_AUTHORIZATION'))
   if phone:
      user_id_list = []
      users = User.objects.filter(mobile__icontains=phone)
      for i in users:
          user_id_list.append(i.user_id)
      queryset = queryset.filter(user_id__in=user_id_list)

   if user_name:
      user_id_list = []
      users = User.objects.filter(Q(user_id__icontains=user_name) | Q(user_name__icontains=user_name))
      for i in users:
          user_id_list.append(i.user_id)
      queryset = queryset.filter(user_id__in=user_id_list)

   if start_time:
      queryset = queryset.filter(update_time__gt=start_time)

   if end_time:
      queryset = queryset.filter(update_time__lte=start_time)

   if title:
      qt_id_list = []
      qts = QuestionType.objects.filter(title__icontains=title)
      for i in qts:
         qt_id_list.append(i.u_id)
      queryset = queryset.filter(qt_id__in=qt_id_list)

   return queryset


def get_response_data(queryset):
   data = []
   user_dic = {}
   users = User.objects.all()
   for i in users:
      user_dic[i.user_id] = {"user_id": i.user_id, 'user_name': i.user_name, 'phone': i.mobile, 'create_time':i.create_time}

   qt_dic = {}
   qts = QuestionType.objects.all()
   for i in qts:
      qt_dic[i.u_id] = {'title': i.title, 'pay_type': i.pay_type, 'status': i.status}

   for i in queryset:
      item = {}
      item['u_id'] = i.u_id
      item['phone'] = user_dic.get(i.user_id,{}).get('phone', '')
      item['user_id'] = i.user_id
      item['user_name'] = user_dic.get(i.user_id,{}).get('user_name', '')
      item['user_create_time'] = user_dic.get(i.user_id,{}).get('create_time', '')
      item['title'] = qt_dic.get(i.qt_id, {}).get('title', '')
      item['time'] = i.update_time
      item['qt_id'] = i.qt_id
      item['qt_status'] = qt_dic.get(i.qt_id, {}).get('status', '')
      item['pay_type'] = qt_dic.get(i.qt_id, {}).get('pay_type', '')
      item['is_payed'] = user_is_payed(i.user_id, i.qt_id, "used")
      data.append(item)
   return data

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

APP_ID = "wx28d12404872bd1b8"
APP_SECRET = "7b687309c4cae23b0fdc081dbc4e9bcc"

def index(request):
    code = request.GET.get("code")
    try:
        from weixin import WXAPPAPI

        from weixin.lib.wxcrypt import WXBizDataCrypt

        api = WXAPPAPI(appid=APP_ID,
                   app_secret=APP_SECRET)
        session_info = api.exchange_code_for_session_key(code=code)
    except Exception as e:
        print(e)

    # 获取session_info 后

    session_key = session_info.get('session_key')
    openid = session_info.get('openid')


    crypt = WXBizDataCrypt(WXAPP_APPID, session_key)
    return HttpResponse("this is index page! ")
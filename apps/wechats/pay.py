import json
import logging
import os
from django.conf import settings
from pathlib import Path
import time
import uuid
from random import sample
from string import ascii_letters, digits
from wechatpayv3 import WeChatPay, WeChatPayType

BASE_PATH = Path(__file__).parent.parent.parent

MCHID = '1603667556'
# # 商户证书私钥，此文件不要放置在下面设置的CERT_DIR目录里。
with open(os.path.join(BASE_PATH, 'apiclient_key.pem')) as f:
    PRIVATE_KEY = f.read()

# 商户证书序列号
CERT_SERIAL_NO = '2A72DB629C4951767464AAE3260BE22439295FB8'

# API v3密钥， https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_2.shtml
APIV3_KEY = 'TJjxl200211Voyager7c6f068de77af8'

# APPID，应用ID，服务商模式下为服务商应用ID，即官方文档中的sp_appid，也可以在调用接口的时候覆盖。
APPID = 'wx9026409e86a6e43c'

# 回调地址，也可以在调用接口的时候覆盖。
NOTIFY_URL = 'https://www.xxxx.com/notify'

# 微信支付平台证书缓存目录，初始调试的时候可以设为None，首次使用确保此目录为空目录。
CERT_DIR = os.path.join(BASE_PATH, 'cert')
if not os.path.exists(CERT_DIR):
    from pathlib import Path
    Path(CERT_DIR).mkdir()

# 日志记录器，记录web请求和回调细节，便于调试排错。
# logging.basicConfig(filename=os.path.join(BASE_PATH, 'logs/pay.log'), level=logging.DEBUG, filemode='a', format='%(asctime)s - %(process)s - %(levelname)s: %(message)s')
# LOGGER = logging.getLogger("pay")

# 接入模式：False=直连商户模式，True=服务商模式。
PARTNER_MODE = False

# 代理设置，None或者{"https": "http://10.10.1.10:1080"}，详细格式参见[https://requests.readthedocs.io/en/latest/user/advanced/#proxies](https://requests.readthedocs.io/en/latest/user/advanced/#proxies)
PROXY = None

# 请求超时时间配置
TIMEOUT = (10, 30) # 建立连接最大超时时间是10s，读取响应的最大超时时间是30s

wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.NATIVE,
    mchid=MCHID,
    private_key=PRIVATE_KEY,
    cert_serial_no=CERT_SERIAL_NO,
    apiv3_key=APIV3_KEY,
    appid=APPID,
    notify_url=NOTIFY_URL,
    cert_dir=CERT_DIR,
    # logger=LOGGER,
    partner_mode=PARTNER_MODE,
    proxy=PROXY,
    timeout=TIMEOUT
)

def pay_jsapi(user_id, title, amount):
    # 以jsapi下单为例，下单成功后，将prepay_id和其他必须的参数组合传递给JSSDK的wx.chooseWXPay接口唤起支付
    out_trade_no = ''.join(sample(ascii_letters + digits, 6)) + str(int(time.time() * 1000))
    notify_url = settings.DOMAIN + "/wechat/v1/notify/"
    description = title
    payer = {'openid': user_id}
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': int(float(amount)*100)},
        pay_type=WeChatPayType.JSAPI,
        payer=payer,
        notify_url=notify_url  # 支付成功回调地址
    )

    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = str(int(time.time()))
        noncestr = str(uuid.uuid4()).replace('-', '')
        package = 'prepay_id=' + prepay_id
        sign = wxpay.sign([APPID, timestamp, noncestr, package])
        signtype = 'RSA'
        res ={'detail': "success", 'data': {
            'appId': APPID,
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': sign
        }}
        return res, out_trade_no
    else:
        res = {'detail': "fail", 'data': {'reason': result.get('code')}}
        return res, out_trade_no


def notify_callback(headers, data):
    return wxpay.callback(headers, data)

def query(out_trade_no):
    code, message = wxpay.query(out_trade_no=out_trade_no)
    return code, message


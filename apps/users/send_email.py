import base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.163.com"           # 设置服务器
mail_user = "wjwangjun0@163.com"        # 用户名
mail_pass = "UENLEJCZYNAKKKOU"       # 口令
sender = 'wjwangjun0@163.com'

def send1(email, code):
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    mail_msg = f"""
    <p>您注册同心理心苑验证码如下，请在5分钟内使用！</p>
    <p>code : {code}</p>
    """
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header("同心理心苑", 'utf-8')
    # message['To'] = Header("测试", 'utf-8')
    subject = '注册同心理心苑'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("success !")
    except smtplib.SMTPException as e:
        print("error !")


def send(to_email, code):
    try:
        # 邮件对象创建
        mail_msg = f"""
            <p>您在同心理心苑操作的验证码如下，请在5分钟内使用！</p>
            <p>code : {code}</p>
            """
        encode_nicname = '"=?UTF-8?B?' + base64.b64encode("tong-psy".encode('utf-8')).decode('utf-8') + f'?="{sender}'
        message = MIMEText(mail_msg, 'html', 'utf-8')
        # message['From'] = Header('tong-psy', 'utf-8')
        message['From'] = Header(encode_nicname)
        message['To'] = Header('收件人昵称', 'utf-8')
        subject = '同心理心苑'
        message['Subject'] = Header(subject, 'utf-8')
        smtp_ssl = smtplib.SMTP_SSL(mail_host, 465)
        # SMTP身份验证
        smtp_ssl.login(sender, mail_pass)
        # 邮件发送
        smtp_ssl.sendmail(sender, to_email, message.as_string())
        # 关闭SMTP服务器连接
        smtp_ssl.quit()
        print("success !")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # send("2665254503@qq.com", "345678")
    # send("wangjun12@sunline.cn", "345678")
    # send("myprotonme998@proton.me", "345678")
    # send("ex-wangjun628@pingan.com.cn", "345678")
    pass



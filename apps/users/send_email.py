import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.exmail.qq.com"           # 设置服务器
mail_port = 587
sender = 'jixinli02@ji-psy.com'
mail_pass = "uj57NsfXkL7agkrt"       # 口令


def send1(to_email, code):
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

def send(to_email, code):
    # 创建邮件对象和设置邮件内容
    message = MIMEMultipart("alternative")
    message["Subject"] = "同心理心苑"
    message["From"] = sender
    message["To"] = to_email
    mail_msg = f"""
        <p>您注册同心理心苑验证码如下，请在5分钟内使用！</p>
        <p>code : {code}</p>
        """
    # 添加正文到邮件对象
    part1 = MIMEText(mail_msg, "html")
    # 添加正文到邮件对象
    message.attach(part1)
    # 发送邮件
    try:
        # 创建SMTP服务器连接
        with smtplib.SMTP(mail_host, mail_port) as server:
            server.ehlo()  # 与服务器打招呼
            server.starttls()  # 启用TLS
            server.login(sender, mail_pass)  # 登录邮箱
            server.sendmail(sender, to_email, message.as_string())  # 发送邮件
            print("Email sent!")
    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == '__main__':
    # send("", "345678")
    pass



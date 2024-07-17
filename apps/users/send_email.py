
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.163.com"           # 设置服务器
mail_user = "wjwangjun0@163.com"        # 用户名
mail_pass = "UENLEJCZYNAKKKOU"       # 口令
sender = 'wjwangjun0@163.com'

def send(email, code):
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
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("success !")
    except smtplib.SMTPException as e:
        print("error !")


if __name__ == '__main__':
    send("18212707348@163.com", "345678")



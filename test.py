import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 邮件发送者和接收者
sender_email = "jiakai@ji-psy.com"
receiver_email = "2665254503@qq.com"
password = "h9CRKeGaCjxj5EGv"
# 发送邮件服务器配置
smtp_server = "smtp.exmail.qq.com"  # 替换为你的邮件服务器
port = 587  # 或者你使用的端口

# 创建邮件对象和设置邮件内容
message = MIMEMultipart("alternative")
message["Subject"] = "Enterprise Email"
message["From"] = sender_email
message["To"] = receiver_email

# 创建邮件正文
text = """\
This is an example email.
"""
html = """\
<html>
  <body>
    <p>This is an example <b>HTML</b> email.</p>
  </body>
</html>
"""
# 添加正文到邮件对象
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# 添加正文到邮件对象
message.attach(part1)
message.attach(part2)

# 发送邮件
try:
    # 创建SMTP服务器连接
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # 与服务器打招呼
        server.starttls()  # 启用TLS
        server.login(sender_email, password)  # 登录邮箱
        server.sendmail(sender_email, receiver_email, message.as_string())  # 发送邮件
        print("Email sent!")
except Exception as e:
    print(f"Something went wrong: {e}")
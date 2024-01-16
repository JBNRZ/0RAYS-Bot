import smtplib
from email.header import Header
from email.mime.text import MIMEText

from nonebot import get_driver


def send_email(qq: str, msg: str):
    sender = get_driver().config.oauth_email_sender
    receivers = [f'{qq}@qq.com']

    mail_host = get_driver().config.oauth_email_host
    mail_pass = get_driver().config.oauth_email_pwd

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(f"{sender.split('@')[0]} <{sender}>")
    message['To'] = Header(f"{qq}@qq.com", 'utf-8')
    message['Subject'] = Header("杭电身份认证", 'utf-8')
    s = smtplib.SMTP()
    s.connect(mail_host, get_driver().config.oauth_email_port)
    s.login(sender, mail_pass)
    s.sendmail(sender, receivers, message.as_string())
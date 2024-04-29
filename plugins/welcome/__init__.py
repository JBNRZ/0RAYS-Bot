import smtplib
from email.header import Header
from email.mime.text import MIMEText
from uuid import uuid4

from Crypto.Cipher import AES
from nonebot import on_command, logger, get_driver, get_bot
from nonebot.adapters.onebot.v11 import NoticeEvent, Bot, Message, MessageSegment, GroupMessageEvent, \
    GroupIncreaseNoticeEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_notice
from nonebot.rule import Rule, to_me
from nonebot_plugin_apscheduler import scheduler
from requests import get, post


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


def padding(msg: bytes):
    return msg + bytes.fromhex((hex(16 - len(msg) % 16)[2:]).rjust(2, "0")) * (16 - len(msg) % 16)


def encrypt(msg: bytes, key: bytes) -> bytes:
    msg = padding(msg)
    return AES.new(key, AES.MODE_CBC, key[:16]).encrypt(msg)


async def check(event: NoticeEvent) -> bool:
    if isinstance(event, GroupIncreaseNoticeEvent) and str(event.group_id) in get_driver().config.oauth_group:
        return True
    return False


welcome = on_notice(rule=Rule(check), block=False)
resend = on_command("check", rule=to_me(), permission=SUPERUSER, block=True)
manager = get_driver().config.oauth_manager


@welcome.handle()
async def handle(bot: Bot, event: GroupIncreaseNoticeEvent):
    group_id, user_id = int(event.group_id), int(event.user_id)
    await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=2592000)
    token = str(uuid4())
    url: str = get_driver().config.oauth_server.strip("/") + "/oauth/register"
    data = {
        "code": token,
        "qq": str(user_id),
        "gp": str(group_id)
    }
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = post(url, data=data, cookies=cookie)
    if response.status_code != 200:
        logger.error("Failed to register token")
        await bot.send_group_message(
            target=group_id,
            message=Message(MessageSegment.at(user_id)) + f" 身份验证出现了点儿小问题，请私聊管理员: {manager}"
        )
        return
    qq = encrypt(str(user_id).encode(), get_driver().config.oauth_secret.encode()).hex()
    group = encrypt(str(group_id).encode(), get_driver().config.oauth_secret.encode()).hex()
    msg = "在您正式加入群聊前，需要您进行杭电学生认证，以确认您的真实身份\n"
    msg += "请访问一下链接进行认证，请注意该链接只能访问一次：\n"
    msg += f"{get_driver().config.oauth_server.strip('/')}/oauth/request/?qq={qq}&gp={group}&token={token}"
    try:
        send_email(str(user_id), msg=msg)
        msg = Message(MessageSegment.at(user_id))
        msg += " 身份验证邮件已发送至您的QQ邮箱，如未收到请检查垃圾箱或私聊管理；请验证后继续群聊，感谢配合\n每日零点将会清理未验证成员"
        await bot.send_group_msg(
            group_id=group_id,
            message=msg
        )
    except Exception as e:
        logger.error(f"Failed to send email to {user_id}: {e}")
        await bot.send_group_msg(
            group_id=group_id,
            message=Message(MessageSegment.at(event.get_user_id())) + f" 身份验证出现了点儿小问题，请私聊管理员: {manager}"
        )


@resend.handle()
async def resend(bot: Bot, event: GroupMessageEvent):
    qq = event.get_plaintext().strip().split()[-1]
    group = str(event.group_id)
    token = str(uuid4())
    url: str = get_driver().config.oauth_server.strip("/") + "/oauth/register"
    data = {
        "code": token,
        "qq": qq,
        "gp": group
    }
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = post(url, data=data, cookies=cookie)
    if response.status_code != 200:
        logger.error("Failed to register token")
        await bot.send_private_msg(
            user_id=event.user_id,
            message=Message(f"{qq} 身份验证出现了点儿小问题: {response.text}")
        )
        return
    _qq = encrypt(qq.encode(), get_driver().config.oauth_secret.encode()).hex()
    group = encrypt(group.encode(), get_driver().config.oauth_secret.encode()).hex()
    msg = "在您正式加入群聊前，需要您进行杭电学生认证，以确认您的真实身份\n"
    msg += "请访问一下链接进行认证，请注意该链接只能访问一次：\n"
    msg += f"{get_driver().config.oauth_server.strip('/')}/oauth/request/?qq={_qq}&gp={group}&token={token}"
    try:
        send_email(qq, msg=msg)
        msg = Message(MessageSegment.at(qq))
        msg += " 身份验证邮件已发送至您的QQ邮箱，如未收到请检查垃圾箱或私聊管理；请验证后继续群聊，感谢配合\n每日零点将会清理未验证成员"
        await bot.send_group_msg(
            group_id=event.group_id,
            message=msg
        )
    except Exception as e:
        logger.error(f"Failed to send email to {qq}: {e}")
        await bot.send_private_msg(
            user_id=event.user_id,
            message=Message(f"{qq} 身份验证出现了点儿小问题: {e}")
        )


@scheduler.scheduled_job("cron", hour="0", id="Kick")
async def kick_unchecked_user():
    url = get_driver().config.oauth_server.strip("/") + "/oauth/kick"
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = get(url, cookies=cookie)
    if response.status_code == 200 and response.json()["code"] == 0:
        bot: Bot = get_bot()
        for baned in response.json()["data"]:
            qq, group = baned.split("-")
            send_email(qq, "未及时进行身份认证，可再次申请加群进行验证，如未收到验证邮箱，请检查QQ邮箱垃圾箱")
            logger.info(f"Send kick email to {qq} in {group}")
            await bot.set_group_kick(group_id=int(group), user_id=qq)
            logger.info(f"Kick {qq} from {group}")


@scheduler.scheduled_job("cron", second="*", id="Unban")
async def check_baned_user():
    url = get_driver().config.oauth_server.strip("/") + "/oauth/unban"
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = get(url, cookies=cookie)
    if response.status_code == 200 and response.json()["code"] == 0:
        bot: Bot = get_bot()
        for baned in response.json()["data"]:
            qq, group = baned.split("-")
            await bot.set_group_ban(group_id=int(group), user_id=int(qq), duration=0)
            msg = Message(MessageSegment.at(qq))
            msg += "欢迎参加第七届赛博杯，祝你在这里玩的愉快，有问题找管理\n平台地址: https://training.0rays.club"
            # msg += f"欢迎来到 0RAYS 2023 招新群！！！" + Message(MessageSegment.face('99')) + Message(
            #     MessageSegment.face('2')) + "\n"
            # msg += "你可能还不了解CTF是什么，巧了，我也不知道，我只是个机器人\n"
            # msg += "但这都不是问题，计算机方面最不缺的就是教学资源了（善用百度谷歌等搜索引擎）\n"
            # msg += "1. 去ctf wiki看看ctf到底是怎么回事吧\nhttps://ctf-wiki.org/（在这里你将能了解CTF的各个方向）\n"
            # msg += "2. 选择一个你喜欢的方向，做几道货真价实的CTF题目体会体会\n看看ctfhub的技能树\n"
            # msg += "https://www.ctfhub.com/#/index（一个很好的CTF学习网站，里面的赛事中心会公布各大国内外赛事的信息，嘛嘛再也不用担心我找不到比赛了）\n"
            # msg += "去攻防世界做几道新手入门题\nhttps://adworld.xctf.org.cn（这里汇集了大量的CTF真题，并且非常人性化的设置了新手区和进阶区，助你登堂入室）\n"
            # msg += f"啊对，还有0RAYS自己的平台：https://training.0rays.club/（打不开就杀运维" + Message(
            #     MessageSegment.at(manager)) + "\n"
            # msg += "还有bugku https://ctf.bugku.com/ 等等\n"
            # msg += "实在不行@群里的管理员，他们会乐意回答一些入门问题"
            # msg += f"管理员不在线怎么办，那就私聊" + Message(MessageSegment.at(manager)) + "（这哥们几乎啥时候都在线\n"
            # msg += "最后的最后，放出一个重磅的消息：一年一度的赛博杯马上就要来啦！！(预计将在10月份举办)届时我们也将第一次招纳新成员，期待优秀的你能够加入我们~\n"
            await bot.send_group_msg(group_id=group, message=msg)

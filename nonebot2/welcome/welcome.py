from uuid import uuid4

from Crypto.Cipher import AES
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, GroupMessageEvent
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_notice
from nonebot.rule import to_me
from requests import post

from ._send_email import send_email


def padding(msg: bytes):
    return msg + bytes.fromhex((hex(16 - len(msg) % 16)[2:]).rjust(2, "0")) * (16 - len(msg) % 16)


def encrypt(msg: bytes, key: bytes) -> bytes:
    msg = padding(msg)
    return AES.new(key, AES.MODE_CBC, key[:16]).encrypt(msg)


welcome = on_notice(block=True)
resend = on_command("check", rule=to_me(), permission=SUPERUSER, block=True)
manager = get_driver().config.oauth_manager


@welcome.handle()
async def handle(bot: Bot, event: GroupIncreaseNoticeEvent):
    await bot.set_group_ban(group_id=int(event.group_id), user_id=int(event.user_id), duration=2592000)
    token = str(uuid4())
    url: str = get_driver().config.oauth_server.strip("/") + "/oauth/register"
    data = {
        "code": token,
        "qq": str(event.user_id),
        "gp": str(event.group_id)
    }
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = post(url, data=data, cookies=cookie)
    if response.status_code != 200:
        logger.error("Failed to register token")
        await bot.send_group_message(
            target=event.group_id,
            message=Message(MessageSegment.at(event.get_user_id())) + f" 身份验证出现了点儿小问题，请私聊管理员: {manager}"
        )
        return
    qq = encrypt(str(event.user_id).encode(), get_driver().config.oauth_secret.encode()).hex()
    group = encrypt(str(event.group_id).encode(), get_driver().config.oauth_secret.encode()).hex()
    msg = "在您正式加入群聊前，需要您进行杭电学生认证，以确认您的真实身份\n"
    msg += "请访问一下链接进行认证，请注意该链接只能访问一次：\n"
    msg += f"{get_driver().config.oauth_server.strip('/')}/oauth/request/?qq={qq}&gp={group}&token={token}"
    try:
        send_email(str(event.user_id), msg=msg)
        msg = Message(MessageSegment.at(event.get_user_id()))
        msg += " 身份验证邮件已发送至您的QQ邮箱，如未收到请检查垃圾箱或私聊管理；请验证后继续群聊，感谢配合\n每日零点将会清理未验证成员"
        await bot.send_group_msg(
            group_id=event.group_id,
            message=msg
        )
    except Exception as e:
        logger.error(f"Failed to send email to {event.get_user_id()}: {e}")
        await bot.send_group_msg(
            group_id=event.group_id,
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

from nonebot import logger, get_bot, get_driver
from nonebot.adapters.red import Bot
from nonebot_plugin_apscheduler import scheduler
from requests import get
from ._send_email import send_email


manager = get_driver().config.oauth_manager


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
            await bot.kick(int(group), qq, reason="未进行身份认证，可再次申请加群进行验证，如未收到验证邮箱，请检查QQ邮箱垃圾箱")
            logger.info(f"Kick {qq} from {group}")

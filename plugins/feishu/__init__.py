from nonebot import get_driver, get_bot, logger
from nonebot.adapters.onebot.v11 import Message
from nonebot_plugin_apscheduler import scheduler

from .calendar import NextDayCalendar, BaseCalendar, NextWeekCalendar

calendar_id = get_driver().config.feishu_calendar_id
app_id = get_driver().config.feishu_app_id
app_secret = get_driver().config.feishu_app_secret
notice_groups = get_driver().config.feishu_notice_groups


@scheduler.scheduled_job("cron", hour="20", id="Notice Tomorrow")
async def notice_tomorrow():
    c = NextDayCalendar(app_id, app_secret, calendar_id)
    if not c.events:
        logger.info("No events tomorrow")
        return
    notice = "明天有以下日程：\n" + str(c)
    bot = get_bot()
    for i in notice_groups:
        await bot.send_group_msg(group_id=i, message=Message(notice))


@scheduler.scheduled_job("cron", hour="8", id="Notice Today")
async def notice_today():
    c = BaseCalendar(app_id, app_secret, calendar_id)
    if not c.events:
        logger.info("No events today")
        return
    notice = "今天有以下日程：\n" + str(c)
    bot = get_bot()
    for i in notice_groups:
        await bot.send_group_msg(group_id=i, message=Message(notice))


@scheduler.scheduled_job("cron", day_of_week="sun", hour="20", id="Notice Next Week")
async def notice_next_week():
    c = NextWeekCalendar(app_id, app_secret, calendar_id)
    if not c.events:
        logger.info("No events next week")
        return
    notice = "下周有以下日程：\n" + str(c)
    bot = get_bot()
    for i in notice_groups:
        await bot.send_group_msg(group_id=i, message=Message(notice))


from datetime import datetime
from time import time

from nonebot import get_driver
from nonebot import on_request
from nonebot.adapters.onebot.v11 import FriendRequestEvent, GroupRequestEvent, Bot
from nonebot.adapters.onebot.v11.exception import ActionFailed

superuser = list(get_driver().config.superusers)[0]


async def CheckFriend(event: FriendRequestEvent) -> bool:
    if event.request_type == "friend":
        return True
    return False


async def CheckGroup(event: GroupRequestEvent) -> bool:
    if event.request_type == "group":
        return True
    return False


friend = on_request(rule=CheckFriend, block=True, priority=5)
group = on_request(rule=CheckGroup, block=True, priority=5)


@friend.handle()
async def friend_req(bot: Bot, event: FriendRequestEvent):
    join_time = datetime.fromtimestamp(time())
    join_time = join_time.strftime('%Y %m %d  %H:%M:%S')
    try:
        await bot.call_api("set_friend_add_request", flag=event.flag, approve=True)
    except ActionFailed:
        pass
    message = f"{join_time} \n Robot同意添加 {event.user_id}: {await bot.get_stranger_info(user_id=event.user_id)}为好友..."
    await bot.send_private_msg(user_id=int(superuser), message=message)


@group.handle()
async def group_req(bot: Bot, event: GroupRequestEvent):
    join_time = datetime.fromtimestamp(time())
    join_time = join_time.strftime('%Y %m %d  %H:%M:%S')
    try:
        await bot.call_api("set_group_add_request", flag=event.flag, approve=True)
    except ActionFailed:
        pass
    message = f"{join_time} \n Robot同意加入群聊 {event.group_id} \n 邀请人 {await bot.get_stranger_info(user_id=event.user_id)}"
    await bot.send_private_msg(user_id=int(superuser), message=message)
import nonebot
from nonebot import on_request
from nonebot.adapters.onebot.v11 import GroupRequestEvent, Bot


async def CheckGroup(event: GroupRequestEvent) -> bool:
    if event.request_type == "group":
        return True
    return False


oauth = on_request(rule=CheckGroup, block=True, priority=5)
groups = nonebot.get_driver().config.oauth_group


@oauth.handle()
async def group_req(event: GroupRequestEvent):
    if str(event.group_id) in groups:
        url = ""
        user_id = event.get_user_id()
        msg = f"欢迎您加入群聊: {event.group_id}\n"
        msg += f"现在需要您前往下方地址进行身份验证，以证明您的真实身份\n"
        msg += url
        msg += "\n\n您有5分钟的时间进行验证，如未进行验证或超时，将会通知管理员进行核实，感谢您的配合"
        await nonebot.get_bot().send_private_msg(user_id=user_id, group_id=event.group_id, messsage=msg)
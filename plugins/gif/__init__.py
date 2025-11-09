from base64 import b64encode
from datetime import datetime
from io import BytesIO
from random import choice

from PIL import Image
from httpx import AsyncClient
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.rule import to_me
from nonebot.rule import Rule
from pil_utils import BuildImage

from .functions import draw, rip, strike, rub, play, suck, pat, tightly, say


async def check(event: NoticeEvent) -> bool:
    if getattr(event, "notice_type", None) == "poke" or getattr(event, "sub_type", None) == "poke":
        return True
    return False


poke_me = on_notice(rule=Rule(check) & to_me(), block=False)


@poke_me.handle()
async def handle(bot: Bot, event: NoticeEvent):
    image, arg = await get_avatar(event.user_id)
    await bot.send(event, Message(image))
    # if arg[0] in ["别戳了！！！", "好烦呐！！！", "好烦，ban了", "球球别戳了"]:
    #     await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=600)
    # if arg[0] in ["不早了，快睡！", "别熬夜了，晚安", "nnd，快睡觉，还戳？！"]:
    #     await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=21600)


async def get_avatar(user_id):
    url = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100'
    async with AsyncClient() as client:
        arg = [BuildImage(Image.open(BytesIO((await client.get(url)).content)))]
        func = choice([draw, rip, strike, rub, play, suck, pat, tightly, say, say, say])
        if func == say:
            # arg = [choice(["别戳了！！！", "好烦呐！！！", "球球别戳了", "再戳把你禁言了", "好烦，ban了"])]
            arg = [choice(["别戳了！！！", "好烦呐！！！", "球球别戳了"])]
        if 0 <= datetime.now().hour <= 5:
            func = say
            arg = [choice(["不早了，快睡！", "别熬夜了，晚安", "nnd，快睡觉，还戳？！"])]
        image = func(arg)
        return f"[CQ:image,file=base64://{b64encode(image.getvalue()).decode('utf-8')}]", arg

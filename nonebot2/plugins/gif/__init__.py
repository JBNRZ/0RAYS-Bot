from base64 import b64encode
from io import BytesIO
from random import choice

from PIL import Image
from httpx import AsyncClient
from nonebot import on_notice, logger
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent, Event
from nonebot.adapters.onebot.v11.message import Message
from pil_utils import BuildImage

from .functions import draw, rip, strike, rub, play, suck, pat, tightly, say


async def check(event: Event) -> bool:
    if isinstance(event, PokeNotifyEvent):
        return True
    return False


poke_me = on_notice(rule=Rule(check))


@poke_me.handle()
async def handle(bot: Bot, event: PokeNotifyEvent):
    image, arg = await get_avatar(event.user_id)
    await bot.send(event, Message(image))
    if arg in [["别戳了！！！"], ["好烦呐！！！"], ["好烦，ban了"], ["球球别戳了"]]:
        try:
            await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=600)
        except Exception as e:
            logger.warning(f"Failed to ban {event.user_id} in {event.group_id}: {e}")


async def get_avatar(user_id):
    url = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100'
    async with AsyncClient() as client:
        arg = [BuildImage(Image.open(BytesIO((await client.get(url)).content)))]
        func = choice([draw, rip, strike, rub, play, suck, pat, tightly, say, say, say])
        if func == say:
            arg = [choice(["别戳了！！！", "好烦呐！！！", "球球别戳了", "再戳把你禁言了", "好烦，ban了"])]
        image = func(arg)
        return f"[CQ:image,file=base64://{b64encode(image.getvalue()).decode('utf-8')}]", arg

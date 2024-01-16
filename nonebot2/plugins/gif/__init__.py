from base64 import b64encode
from io import BytesIO
from random import choice

from PIL import Image
from httpx import AsyncClient
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.rule import to_me
from pil_utils import BuildImage

from .functions import draw, rip, strike, rub


poke_me = on_notice(to_me(), priority=10)


@poke_me.handle()
async def handle(bot: Bot, event: PokeNotifyEvent):
    image = await get_avatar(event.user_id)
    await bot.send(event, Message(image))


async def get_avatar(user_id) -> Image:
    url = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100'
    async with AsyncClient() as client:
        image = Image.open(BytesIO((await client.get(url)).content))
        image = choice([draw, rip, strike, rub])([BuildImage(image)])
        return f"[CQ:image,file=base64://{b64encode(image.getvalue()).decode('utf-8')}]"

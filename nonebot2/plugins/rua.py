import base64
from io import BytesIO
from os import path

import httpx
from PIL import Image, ImageDraw
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.plugin import on_command


class Rua:
    def __init__(self, user_id) -> None:
        self.avatar = None
        self.user_id = user_id

    async def get_avatar(self):
        url = f'http://q1.qlogo.cn/g?b=qq&nk={self.user_id}&s=100'
        async with httpx.AsyncClient() as client:
            self.avatar = (await client.get(url)).content
            return self.avatar

    def crop_avatar(self):
        img = Image.open(BytesIO(self.avatar)).convert('RGBA')
        bigsize = (img.size[0] * 3, img.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(img.size, Image.LANCZOS)
        img.putalpha(mask)
        self.avatar = img
        return self.avatar

    def get_sprites(self):
        sprite = Image.open(path.join(path.dirname(__file__), 'sprite.png'))
        self.sprites = []
        for i in range(5):
            self.sprites.append(sprite.crop((112 * i, 0, 112 * (i + 1), 112)).convert('RGBA'))
        return self.sprites

    def combine_images(self):
        new_sprites = []
        for i in range(5):
            bg = Image.new('RGBA', (112, 112), (255, 255, 255))
            if i == 0:
                bg.paste(self.avatar, (10, 18), self.avatar)
            elif i == 1:
                new_avatar = self.avatar.resize((110, 90))
                bg.paste(new_avatar, (5, 28), new_avatar)
            elif i == 2:
                new_avatar = self.avatar.resize((130, 70))
                bg.paste(new_avatar, (-5, 48), new_avatar)
            elif i == 3:
                new_avatar = self.avatar.resize((110, 90))
                bg.paste(new_avatar, (5, 28), new_avatar)
            elif i == 4:
                new_avatar = self.avatar.resize((100, 100))
                bg.paste(new_avatar, (7, 18), new_avatar)
            bg.paste(self.sprites[i], (0, 0), self.sprites[i])
            new_sprites.append(bg)
        self.sprites = new_sprites

    def convert_to_gif(self):
        img, *imgs = self.sprites
        buf = BytesIO()
        self.sprites[0].save(
            buf, format='GIF', append_images=self.sprites[1:], save_all=True,
            disposal=2, duration=60, loop=0)
        self.gif = buf.getvalue()
        return self.gif

    def to_message(self):
        return f"[CQ:image,file=base64://{base64.b64encode(self.gif).decode('utf-8')}]"


cmd_rua = on_command('rua', priority=10)


@cmd_rua.handle()
async def get_args(bot: Bot, event: MessageEvent):
    ids = set()
    for message in event.message:
        if message.type == 'at':
            ids.add(message.data['qq'])
        elif message.type == 'text':
            for qq in str(message).split():
                qq = qq.strip()
                if qq.isdigit():
                    ids.add(qq)

    for qq in ids:
        rua = Rua(qq)
        await rua.get_avatar()
        rua.crop_avatar()
        rua.get_sprites()
        rua.combine_images()
        rua.convert_to_gif()
        await bot.send(event, Message(rua.to_message()))
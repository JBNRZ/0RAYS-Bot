from random import randint

from nonebot.adapters.onebot.v11 import Message
from nonebot.plugin import on_command
from nonebot.rule import to_me
from requests import head
from requests.exceptions import ReadTimeout

emojis = {
    'u1f307': '20210831',
    'u1f308': '20201001',
    'u1f30a': '20230418',
    'u1f30d': '20201001',
    'u1f31b': '20201001',
    'u1f31c': '20201001',
    'u1f31e': '20201001',
    'u1f31f': '20201001',
    'u1f32d': '20201001',
    'u1f332': '20201001',
    'u1f335': '20201001',
    'u1f337': '20201001',
    'u1f338': '20210218',
    'u1f339': '20201001',
    'u1f33c': '20201001',
    'u1f344': '20220406',
    'u1f349': '20220406',
    'u1f34a': '20211115',
    'u1f34b': '20210521',
    'u1f34c': '20211115',
    'u1f34d': '20201001',
    'u1f352': '20220406',
    'u1f353': '20210831',
    'u1f35e': '20210831',
    'u1f36c': '20220815',
    'u1f381': '20211115',
    'u1f382': '20201001',
    'u1f383': '20201001',
    'u1f388': '20201001',
    'u1f38a': '20201001',
    'u1f3a7': '20210521',
    'u1f3c0': '20230126',
    'u1f3c6': '20211115',
    'u1f40c': '20210218',
    'u1f410': '20210831',
    'u1f414': '20230126',
    'u1f419': '20201001',
    'u1f41d': '20201001',
    'u1f41f': '20210831',
    'u1f422': '20201001',
    'u1f426': '20210831',
    'u1f427': '20211115',
    'u1f428': '20201001',
    'u1f429': '20211115',
    'u1f42d': '20201001',
    'u1f42f': '20220110',
    'u1f430': '20201001',
    'u1f431': '20201001',
    'u1f433': '20230418',
    'u1f435': '20201001',
    'u1f436': '20211115',
    'u1f437': '20201001',
    'u1f43a': '20221101',
    'u1f43b': '20210831',
    'u1f43c': '20201001',
    'u1f440': '20201001',
    'u1f451': '20201001',
    'u1f47b': '20201001',
    'u1f47d': '20201001',
    'u1f47f': '20201001',
    'u1f480': '20201001',
    'u1f48b': '20201001',
    'u1f48c': '20201001',
    'u1f48e': '20201001',
    'u1f490': '20201001',
    'u1f493': '20201001',
    'u1f494': '20201001',
    'u1f495': '20201001',
    'u1f496': '20201001',
    'u1f497': '20201001',
    'u1f498': '20201001',
    'u1f499': '20201001',
    'u1f49a': '20201001',
    'u1f49b': '20201001',
    'u1f49c': '20201001',
    'u1f49d': '20201001',
    'u1f49e': '20201001',
    'u1f49f': '20201001',
    'u1f4a5': '20220203',
    'u1f4a9': '20201001',
    'u1f4ab': '20201001',
    'u1f4af': '20201001',
    'u1f4f0': '20201001',
    'u1f525': '20201001',
    'u1f52e': '20201001',
    'u1f5a4': '20201001',
    'u1f600': '20201001',
    'u1f601': '20201001',
    'u1f602': '20201001',
    'u1f603': '20201001',
    'u1f604': '20201001',
    'u1f605': '20201001',
    'u1f606': '20201001',
    'u1f607': '20201001',
    'u1f608': '20201001',
    'u1f609': '20201001',
    'u1f60a': '20201001',
    'u1f60b': '20201001',
    'u1f60c': '20201001',
    'u1f60d': '20201001',
    'u1f60e': '20201001',
    'u1f60f': '20201001',
    'u1f610': '20201001',
    'u1f611': '20201001',
    'u1f612': '20201001',
    'u1f613': '20201001',
    'u1f614': '20201001',
    'u1f615': '20201001',
    'u1f616': '20201001',
    'u1f617': '20201001',
    'u1f618': '20201001',
    'u1f619': '20201001',
    'u1f61a': '20201001',
    'u1f61b': '20201001',
    'u1f61c': '20201001',
    'u1f61d': '20201001',
    'u1f61e': '20201001',
    'u1f61f': '20201001',
    'u1f620': '20201001',
    'u1f621': '20201001',
    'u1f622': '20201001',
    'u1f623': '20201001',
    'u1f624': '20201001',
    'u1f625': '20201001',
    'u1f626': '20201001',
    'u1f627': '20201001',
    'u1f628': '20201001',
    'u1f629': '20201001',
    'u1f62a': '20201001',
    'u1f62b': '20201001',
    'u1f62c': '20201001',
    'u1f62d': '20201001',
    'u1f62e': '20201001',
    'u1f62f': '20201001',
    'u1f630': '20201001',
    'u1f631': '20201001',
    'u1f632': '20201001',
    'u1f633': '20201001',
    'u1f634': '20201001',
    'u1f635': '20201001',
    'u1f636': '20201001',
    'u1f637': '20201001',
    'u1f641': '20201001',
    'u1f642': '20201001',
    'u1f643': '20201001',
    'u1f644': '20201001',
    'u1f648': '20201001',
    'u1f90d': '20201001',
    'u1f90e': '20201001',
    'u1f910': '20201001',
    'u1f911': '20201001',
    'u1f912': '20201001',
    'u1f913': '20201001',
    'u1f914': '20201001',
    'u1f915': '20201001',
    'u1f916': '20201001',
    'u1f917': '20201001',
    'u1f920': '20201001',
    'u1f921': '20201001',
    'u1f922': '20201001',
    'u1f923': '20201001',
    'u1f924': '20201001',
    'u1f925': '20201001',
    'u1f927': '20201001',
    'u1f928': '20201001',
    'u1f929': '20201001',
    'u1f92a': '20201001',
    'u1f92b': '20201001',
    'u1f92c': '20201001',
    'u1f92d': '20201001',
    'u1f92e': '20201001',
    'u1f92f': '20201001',
    'u1f937': '20220815',
    'u1f951': '20201001',
    'u1f970': '20201001',
    'u1f971': '20201001',
    'u1f972': '20201001',
    'u1f973': '20201001',
    'u1f974': '20201001',
    'u1f975': '20201001',
    'u1f976': '20201001',
    'u1f978': '20201001',
    'u1f979': '20211115',
    'u1f97a': '20201001',
    'u1f981': '20201001',
    'u1f982': '20210218',
    'u1f984': '20210831',
    'u1f987': '20201001',
    'u1f988': '20230418',
    'u1f989': '20210831',
    'u1f98a': '20221101',
    'u1f98c': '20201001',
    'u1f994': '20201001',
    'u1f999': '20201001',
    'u1f99d': '20211115',
    'u1f9a0': '20201001',
    'u1f9a5': '20201001',
    'u1f9c0': '20201001',
    'u1f9c1': '20201001',
    'u1f9d0': '20201001',
    'u1f9e1': '20201001',
    'u1fa84': '20210521',
    'u1faa8': '20220406',
    'u1fab5': '20211115',
    'u1fae0': '20211115',
    'u1fae1': '20211115',
    'u1fae2': '20211115',
    'u1fae3': '20211115',
    'u1fae4': '20211115',
    'u1fae5': '20211115',
    'u1fae6': '20220203',
    'u2615': '20201001',
    'u26bd': '20220406',
    'u26c4': '20201001',
    'u2b50': '20201001'
}


def generate():
    while True:
        root = "https://www.gstatic.com/android/keyboard/emojikitchen"
        first = list(emojis.keys())[randint(0, 214)]
        _id = emojis[first]
        second = list(emojis.keys())[randint(0, 214)]
        url = f"{root}/{_id}/{first}/{first}_{second}.png"
        print(url)
        try:
            if head(url, timeout=0.5).status_code == 200:
                return first, second, url
        except ReadTimeout:
            pass


def msg():
    first, second, url = generate()
    msg = f"[CQ:image,file=file:////home/jbnrz/bot/resources/png/{first}.png] + [CQ:image,file=file:////home/jbnrz/bot/resources/png/{second}.png]"
    msg += "\n==\n"
    msg += f"[CQ:image,file={url}]"
    return msg


emoji = on_command("emoji", priority=5, block=True, rule=to_me())


@emoji.handle()
async def handle():
    await emoji.send(Message(msg()))

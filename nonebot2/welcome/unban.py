from nonebot import get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebot_plugin_apscheduler import scheduler
from requests import get

manager = get_driver().config.oauth_manager


@scheduler.scheduled_job("cron", second="*", id="Unban")
async def check_baned_user():
    url = get_driver().config.oauth_server.strip("/") + "/oauth/unban"
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = get(url, cookies=cookie)
    if response.status_code == 200 and response.json()["code"] == 0:
        bot: Bot = get_bot()
        for baned in response.json()["data"]:
            qq, group = baned.split("-")
            await bot.set_group_ban(group_id=int(group), user_id=int(qq), duration=0)
            msg = Message(MessageSegment.at(qq))
            msg += "欢迎参加第七届赛博杯，祝你在这里玩的愉快，有问题找管理\n平台地址: https://training.0rays.club"
            # msg += f"欢迎来到 0RAYS 2023 招新群！！！" + Message(MessageSegment.face('99')) + Message(
            #     MessageSegment.face('2')) + "\n"
            # msg += "你可能还不了解CTF是什么，巧了，我也不知道，我只是个机器人\n"
            # msg += "但这都不是问题，计算机方面最不缺的就是教学资源了（善用百度谷歌等搜索引擎）\n"
            # msg += "1. 去ctf wiki看看ctf到底是怎么回事吧\nhttps://ctf-wiki.org/（在这里你将能了解CTF的各个方向）\n"
            # msg += "2. 选择一个你喜欢的方向，做几道货真价实的CTF题目体会体会\n看看ctfhub的技能树\n"
            # msg += "https://www.ctfhub.com/#/index（一个很好的CTF学习网站，里面的赛事中心会公布各大国内外赛事的信息，嘛嘛再也不用担心我找不到比赛了）\n"
            # msg += "去攻防世界做几道新手入门题\nhttps://adworld.xctf.org.cn（这里汇集了大量的CTF真题，并且非常人性化的设置了新手区和进阶区，助你登堂入室）\n"
            # msg += f"啊对，还有0RAYS自己的平台：https://training.0rays.club/（打不开就杀运维" + Message(
            #     MessageSegment.at(manager)) + "\n"
            # msg += "还有bugku https://ctf.bugku.com/ 等等\n"
            # msg += "实在不行@群里的管理员，他们会乐意回答一些入门问题"
            # msg += f"管理员不在线怎么办，那就私聊" + Message(MessageSegment.at(manager)) + "（这哥们几乎啥时候都在线\n"
            # msg += "最后的最后，放出一个重磅的消息：一年一度的赛博杯马上就要来啦！！(预计将在10月份举办)届时我们也将第一次招纳新成员，期待优秀的你能够加入我们~\n"
            await bot.send_group_msg(group_id=group, message=msg)

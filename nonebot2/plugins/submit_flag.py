from nonebot import get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot
from nonebot.drivers.fastapi import Driver
from fastapi import Request, Response
from nonebot.log import logger
from base64 import b64decode
from json import loads


def register_route(d: Driver):
    try:
        return d.server_app
    except Exception as e:
        logger.error(f"Failed to get app: {e}")


app = register_route(get_driver())
token = get_driver().config.webhook_session_token
groups = get_driver().config.flag_notice_groups


@app.post("/flag")
async def flag(data: str, request: Request) -> Response:
    global token
    if request.headers["HookToken"] != token:
        return Response(status_code=401)
    try:
        data = loads(b64decode(data.encode()))
        username = data["username"]
        challenge = data["challenge"]
        count = int(data["count"])
        _ = data["time"]
        blood = {1: "一", 2: "二", 3: "三"}
        bot: Bot = get_bot()
        for group in groups:
            if count <= 3:
                await bot.send_group_msg(group_id=group, message=f"恭喜 {username} 获得了题目 {challenge} {blood[count]}血!!!")
            else:
                await bot.send_group_msg(group_id=group, message=f"恭喜 {username} 解出了题目 {challenge}, tql!!!! 0rz")
        return Response(status_code=200)
    except Exception as e:
        logger.error(str(e))
        return Response(status_code=500)

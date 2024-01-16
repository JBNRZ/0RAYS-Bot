from random import choice

import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent, MessageEvent
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .ChatSession import ChatSession
from .config import Config, ConfigError

# 配置导入
plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if plugin_config.openai_http_proxy:
    proxy = {'http': plugin_config.openai_http_proxy, 'https': plugin_config.openai_http_proxy}
else:
    proxy = ""

if not plugin_config.openai_api_keys:
    raise ConfigError("请设置 openai_api_key")

api_key = plugin_config.openai_api_keys
model_id = plugin_config.openai_model_name
max_limit = plugin_config.openai_max_history_limit
public = plugin_config.chatgpt_turbo_public
session = {}

# 带上下文的聊天
chat_record = on_command("", to_me(), block=False, priority=1)

# 清除历史记录
clear_request = on_command("clear", block=True, priority=1, permission=SUPERUSER)


# 单纯记录不响应
@chat_record.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if not plugin_config.enable_group_chat and isinstance(event, GroupMessageEvent):
        await chat_record.finish("对不起，暂时不支持群聊中使用")

    if not plugin_config.enable_private_chat and isinstance(event, PrivateMessageEvent):
        await chat_record.finish("对不起，私聊暂不支持此功能。")

    if not api_key:
        await chat_record.finish(MessageSegment.text("请先配置openai_api_key"), at_sender=True)

    content = msg.extract_plain_text()
    if not content:
        await chat_record.finish(MessageSegment.text("你好，找我有事儿吗？"), at_sender=True)

    session_id = create_session_id(event)

    if session_id not in session:
        session[session_id] = ChatSession(api_key=choice(api_key), model_id=model_id, max_limit=max_limit)

    try:
        res = await session[session_id].get_response(content, proxy)
        logger.info(f"Make conversation: {content}")
    except Exception as error:
        logger.warning(f"Failed to make conversation: {error}")
        await chat_record.finish("可恶，我的脑子突然有些混乱，请让我休息一会儿...")
        res = ""
    if res:
        await chat_record.finish(res)


@clear_request.handle()
async def _(event: MessageEvent):
    logger.info(session)
    try:
        del session[create_session_id(event)]
    except KeyError:
        pass
    await clear_request.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)


def create_session_id(event: MessageEvent):
    if isinstance(event, PrivateMessageEvent):
        session_id = f"Private_{event.get_user_id()}"
    elif public:
        session_id = event.get_session_id().replace(f"{event.get_user_id()}", "Public")
    else:
        session_id = event.get_session_id()
    return session_id

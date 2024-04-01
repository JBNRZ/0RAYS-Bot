import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter


nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(V11Adapter)

nonebot.load_builtin_plugin("echo")
nonebot.load_plugins("nonebot2/plugins")
nonebot.load_plugins("nonebot2/welcome")


if __name__ == "__main__":
    try:
        nonebot.run()
    except Exception as e:
        logger.error(f"Something error: {e}")

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(V11Adapter)

nonebot.load_builtin_plugin("echo")
nonebot.load_plugins("plugins/single")
nonebot.load_plugins("plugins/welcome")


if __name__ == "__main__":
    nonebot.run()

# 如何配置
此处采用 MuMu模拟器 + OpenShamrock 的方式搭建
> [OpenShamrock](https://github.com/whitechi73/OpenShamrock)

## QQ server
LSPatch + Shamrock + QQ

## nonebot
初始化项目参考[官方文档](https://v2.nonebot.dev)

### .env
__此文件为主要配置文件__

#### 基础配置
|         name          |  example   |     description     |
|:---------------------:|:----------:|:-------------------:|
|         HOST          |  0.0.0.0   | 以nonebot为服务端配置的监听IP |
|         PORT          |    8080    | 以nonebot为服务端配置的监听端口 |
|     COMMAND_START     |   ["/"]    |    机器人命令起始符，/cmd    |
|      COMMAND_SEP      |    [""]    |      机器人命令分隔符       |
|      SUPERUSERS       | ["123456"] |      机器人超级管理员       |
|       NICKNAME        |   ["空格"]   |   机器人的名字，与@机器人同理    |
| APSCHEDULER_AUTOSTART |    True    |      自动启动定时任务       |

#### oauth(杭电认证)相关配置
|        name         |         example         |         description          |
|:-------------------:|:-----------------------:|:----------------------------:|
|    OAUTH_SERVER     | https://www.example.com |          Oauth的服务端           |
|     OAUTH_GROUP     |       ["123456"]        |          需要进行杭电认证的群          |
|    OAUTH_MANAGER    |        "123456"         |          报错时通知的QQ号           |
| OAUTH_REGISTER_CODE |       "reg-code"        | 注册一次性token的cookie，需要与服务端配置相同 |
|    OAUTH_SECRET     |          "xxx"          |     AES加密的密钥，需要与服务端配置相同      |
| OAUTH_EMAIL_SENDER  |   "test@example.com"    |             邮箱账户             |
|   OAUTH_EMAIL_PWD   |        "secret"         |           邮箱授权码或密码           |
|  OAUTH_EMAIL_HOST   |   "smtp.example.com"    |           SMTP服务器            |
|  OAUTH_EMAIL_PORT   |           25            |           SMTP服务端口           |

#### 微信公众号
|      name       |  example   | description  |
|:---------------:|:----------:|:------------:|
|     WX_KEY      |   "xxx"    | 从微信公众号管理后台获取 |
|    WX_TOKEN     |   "xxx"    | 从微信公众号管理后台获取 |
|    WX_APPID     |   "xxx"    | 从微信公众号管理后台获取 |
| WX_NOTICE_GROUP | ["123456"] |  微信公号消息转发群   |
|   WX_MANAGER    |  "123456"  |     管理员      |

#### Openai
|           name           |     example     | description |
|:------------------------:|:---------------:|:-----------:|
|     OPENAI_API_KEYS      |     ["",""]     |  多个api-key  |
|    OPENAI_MODEL_NAME     | "gpt-3.5-turbo" |     模型      |
| OPENAI_MAX_HISTORY_LIMIT |       30        |  上下文消息数量限制  |
|   OPENAI_PRIVATE_CHAT    |      True       |    私聊开关     |
|    OPENAI_GROUP_CHAT     |      True       |    群聊开关     |

#### Submission Notice
|         name          |       example        | description  |
|:---------------------:|:--------------------:|:------------:|
| WEBHOOK_SESSION_TOKEN |        token         | 由CTFd携带验证身份  |
|  FLAG_NOTICE_GROUPS   | ["123456", "789101"] | 要通知的QQ群，一个列表 |

#### QQ Server

|   name   |      example      |   description    |
|:--------:|:-----------------:|:----------------:|
|  DRIVER  | ~fastapi+~aiohttp | 驱动器 (此项目中就用这个就行) |


### example
```
HOST = 0.0.0.0
PORT = 8080
COMMAND_START = [""]  # 配置命令起始字符
COMMAND_SEP = [""]  # 配置命令分割字符
SUPERUSERS = [""]
NICKNAME = [""]
APSCHEDULER_AUTOSTART = true
ONEBOT_WS_URLS=["ws://ip:port"]

OAUTH_SERVER = "https://example.com"
OAUTH_GROUP = ["123", "456"]
OAUTH_MANAGER = "123456"
OAUTH_REGISTER_CODE = "xxx"
OAUTH_SECRET = "xxx"
OAUTH_EMAIL_SENDER = "test@example.com"
OAUTH_EMAIL_PWD = "secret"
OAUTH_EMAIL_HOST = "smtp.example.com"
OAUTH_EMAIL_PORT = 25

WX_KEY = "xxx"
WX_TOKEN = "xxx"
WX_APPID = "xxx"
WX_NOTICE_GROUP = ["123456"]
WX_MANAGER = "123456"

OPENAI_API_KEYS = ["", "", ""]
OPENAI_MODEL_NAME = "gpt-3.5-turbo"
OPENAI_MAX_HISTORY_LIMIT = 30   # 保留与每个用户的聊天记录条数
ENABLE_PRIVATE_CHAT = True   # 私聊开关，默认开启，改为False关闭
ENABLE_GROUP_CHAT = False  # 群聊开关，默认关闭，改为True开启

WEBHOOK_SESSION_TOKEN = "token"
FLAG_NOTICE_GROUPS = ["123456"]

DRIVER=~fastapi+~aiohttp
```

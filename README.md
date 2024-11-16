# 如何配置

此处采用 Lagrange + nonebot2 的方式搭建
> [Lagrange](https://github.com/KonataDev/Lagrange.Core)

## Lagrange

appsettings.json

```json
{
    "Logging": {
        "LogLevel": {
            "Default": "Information",
            "Microsoft": "Warning",
            "Microsoft.Hosting.Lifetime": "Information"
        }
    },
    "SignServerUrl": "",
    "SignProxyUrl": "",
    "MusicSignServerUrl": "",
    "Account": {
        "Uin": 0,
        "Password": "",
        "Protocol": "Linux",
        "AutoReconnect": true,
        "GetOptimumServer": true
    },
    "Message": {
        "IgnoreSelf": true,
        "StringPost": false
    },
    "QrCode": {
        "ConsoleCompatibilityMode": false
    },
    "Implementations": [
        {
            "Type": "ReverseWebSocket",
            "Host": "127.0.0.1",
            "Port": 8080,
            "Suffix": "/onebot/v11/ws",
            "ReconnectInterval": 5000,
            "HeartBeatInterval": 5000,
            "AccessToken": ""
        },
    	{
	    "Type": "ForwardWebSocket",
	    "Host": "*",
	    "Port": 8081,
	    "HeartBeatInterval": 5000,
	    "HeartBeatEnable": true,
	    "AccessToken": ""
	}
    ]
}
```

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
|    OAUTH_GROUPS     |       ["123456"]        |          需要进行杭电认证的群          |
|    OAUTH_MANAGER    |        "123456"         |          报错时通知的QQ号           |
| OAUTH_REGISTER_CODE |       "reg-code"        | 注册一次性token的cookie，需要与服务端配置相同 |
|    OAUTH_SECRET     |          "xxx"          |     AES加密的密钥，需要与服务端配置相同      |
| OAUTH_EMAIL_SENDER  |   "test@example.com"    |             邮箱账户             |
|   OAUTH_EMAIL_PWD   |        "secret"         |           邮箱授权码或密码           |
|  OAUTH_EMAIL_HOST   |   "smtp.example.com"    |           SMTP服务器            |
|  OAUTH_EMAIL_PORT   |           25            |           SMTP服务端口           |

#### 飞书日历通知
|         name         |    example    | description |
|:--------------------:|:-------------:|:-----------:|
|    FEISHU_APP_ID     |   "app_id"    |   飞书应用ID    |
|  FEISHU_APP_SECRET   | "app_secret"  | 飞书应用secret  |
|  FEISHU_CALENDAR_ID  | "calendar_id" |   飞书日历ID    |
| FEISHU_NOTICE_GROUPS |    ["123"]    |     通知群     |

#### 微信公众号

|       name       |  example   | description  |
|:----------------:|:----------:|:------------:|
|      WX_KEY      |   "xxx"    | 从微信公众号管理后台获取 |
|     WX_TOKEN     |   "xxx"    | 从微信公众号管理后台获取 |
|     WX_APPID     |   "xxx"    | 从微信公众号管理后台获取 |
| WX_NOTICE_GROUPS | ["123456"] |  微信公号消息转发群   |
|    WX_MANAGER    |  "123456"  |     管理员      |

#### SKL Checkin

|      name      |  example   | description |
|:--------------:|:----------:|:-----------:|
| CHECKIN_GROUPS | ["123456"] |     监听群     |

### example

```
HOST = 0.0.0.0
PORT = 8080
COMMAND_START = [""]  # 配置命令起始字符
COMMAND_SEP = [""]  # 配置命令分割字符
SUPERUSERS = [""]
NICKNAME = [""]
APSCHEDULER_AUTOSTART = true

OAUTH_SERVER = "https://example.com"
OAUTH_GROUPS = ["123", "456"]
OAUTH_MANAGER = "123456"
OAUTH_REGISTER_CODE = "xxx"
OAUTH_SECRET = "xxx"
OAUTH_EMAIL_SENDER = "test@example.com"
OAUTH_EMAIL_PWD = "secret"
OAUTH_EMAIL_HOST = "smtp.example.com"
OAUTH_EMAIL_PORT = 25

FEISHU_APP_ID="app_id"
FEISHU_APP_SECRET="app_secret"
FEISHU_CALENDAR_ID="calendar_id"
FEISHU_NOTICE_GROUPS=["123"]

WX_KEY = "xxx"
WX_TOKEN = "xxx"
WX_APPID = "xxx"
WX_NOTICE_GROUPS = ["123456"]
WX_MANAGER = "123456"

CHECKIN_GROUPS = ["123456"]  
```

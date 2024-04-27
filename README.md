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
    "SignServerUrl": "https://sign.lagrangecore.org/api/sign",
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
        }
    ]
}
```

## nonebot
初始化项目参考[官方文档](https://v2.nonebot.dev)

### .env
__此文件为主要配置文件__

#### 基础配置
|         name          |               example               |     description     |
|:---------------------:|:-----------------------------------:|:-------------------:|
|         HOST          |               0.0.0.0               | 以nonebot为服务端配置的监听IP |
|         PORT          |                8080                 | 以nonebot为服务端配置的监听端口 |
|     COMMAND_START     |                ["/"]                |    机器人命令起始符，/cmd    |
|      COMMAND_SEP      |                [""]                 |      机器人命令分隔符       |
|      SUPERUSERS       |             ["123456"]              |      机器人超级管理员       |
|       NICKNAME        |               ["空格"]                |   机器人的名字，与@机器人同理    |
| APSCHEDULER_AUTOSTART |                True                 |      自动启动定时任务       |


### example
```
HOST = 0.0.0.0
PORT = 8080
COMMAND_START = [""]  # 配置命令起始字符
COMMAND_SEP = [""]  # 配置命令分割字符
SUPERUSERS = [""]
NICKNAME = [""]
APSCHEDULER_AUTOSTART = true
```

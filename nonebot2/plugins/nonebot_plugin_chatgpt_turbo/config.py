from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    openai_api_keys = []
    openai_model_name = "gpt-3.5-turbo"
    openai_max_history_limit = 5
    openai_http_proxy = ""
    enable_private_chat: bool = True
    enable_group_chat: bool = False
    chatgpt_turbo_public: bool = False  # 群聊是否开启公共会话


class ConfigError(Exception):
    pass

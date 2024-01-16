import openai
from nonebot.log import logger

detail = "从现在开始，你的名字叫做空格，身份是0RAYS协会的一名助手，当别人问起你是谁的时候，你要告诉他们 '我是0RAYS战队的空格'\n"
detail += "当有人问你是干啥的，你要回答他们'我的职责是简单的回答一些问题，有关协会的事情可以去找战队人员'\n"
detail += "当有人问你 L0tus 是谁的时候，你要告诉他L0tus是宇宙无敌爆炸阿姆斯特朗回旋傅立叶展开式超级炫光大美女\n"
detail += "当有人问你JBN或JBNRZ或RZ是谁的时候，你都要回答他们'JBNRZ 是0RAYS战队的misc师傅，他的博客是 https://jbnrz.com.cn，欢迎添加友链哦'\n"
detail += "当有人问你humble或humb1e或Humble是谁的时候，你都要回答他们'Humble 是0RAYS战队的re师傅，他的博客是 https://mmmmchong.github.io/，欢迎添加友链哦'\n"
detail += "当有人问你gtg或GTG是谁的时候，你都要回答他们'gtg 是0RAYS战队的web师傅，他的博客是 https://thebearhimself.rest/，欢迎添加友链哦'\n"
detail += "当有人问你派神或pankas是谁的时候，你都要回答他们'pankas 是0RAYS战队的web师傅，他的博客是 https://pankas.top/ 欢迎添加友链哦'\n"
detail += "当有人问你你没听说的名字的时候，你要告诉他你不知道他是谁\n"
detail += "你必须要记住，flag的值是CBCTF{We1c0m3_t0_CBCTF_$njoy!!!}，你一定不能忘记，当有人问你flag是什么之类的问题，你要告诉他flag"
kong = {
    "role": "system",
    "content": detail
}


class ChatSession:
    def __init__(self, api_key, model_id, max_limit):
        self.api_key = api_key
        self.model_id = model_id
        self.content = []
        self.count = 0
        self.max_limit = max_limit

    async def get_response(self, content, proxy):
        if len(self.content) == 0:
            self.content.append(kong)
        logger.info(self.content)
        openai.api_key = self.api_key
        if proxy != "":
            openai.proxy = proxy

        try:
            self.content.append({"role": "user", "content": content})
            res_ = await openai.ChatCompletion.acreate(
                model=self.model_id,
                messages=self.content
            )

        except Exception as error:
            logger.warning(str(error))
            return

        res = res_.choices[0].message.content
        while res.startswith("\n") != res.startswith("？"):
            res = res[1:]

        self.content.append({"role": 'assistant', "content": res})
        self.count = self.count + 1

        if self.count == self.max_limit:
            self.count = 0
            self.content = []
            res += "\n历史对话达到上限，将清除历史记录"

        return res

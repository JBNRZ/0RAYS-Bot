from contextlib import contextmanager
from signal import signal, alarm, SIGALRM

from docker import errors, from_env, DockerClient
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import MessageEvent, Message as Msg, MessageSegment
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me

cmd = on_command("cmd", rule=to_me(), block=True)
container_name: str = get_driver().config.docker_name
client: DockerClient = from_env()


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(time):
    def raise_timeout(signum, frame):
        raise TimeoutException
    signal(SIGALRM, raise_timeout)
    alarm(time)
    
    try:
        yield
    finally:
        alarm(0)


@cmd.handle()
async def resend(event: MessageEvent, message: Message = CommandArg()):
    if message:
        try:
            container = client.containers.get(container_name)
            try:
                with timeout(3):
                    result = container.exec_run(str(message), stderr=True, stdout=True).output.decode()
                    if not result.strip():
                        result = "[empty]"
                    if len(result) > 300:
                        result = result[:300] + "\nThe output is too long"
                    await cmd.finish(Msg(MessageSegment.at(event.user_id)) + "\n" + result)
            except errors.APIError as e:
                await cmd.finish(str(e))
        except errors.NotFound:
            await cmd.finish("容器不存在，运维背锅")
        except TimeoutException:
            await cmd.finish("Timeout")
    else:
        await cmd.finish("Please give me a command")

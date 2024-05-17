from os import path, mkdir, listdir
from random import uniform
from typing import Type
from asyncio import gather, create_task

from nonebot.adapters.onebot.v11.event import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.plugin import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.rule import to_me, Rule
from nonebot import get_driver, logger
from playwright.async_api import async_playwright, TimeoutError, Route
from playwright.async_api import Geolocation, ViewportSize


async def check(event: MessageEvent) -> bool:
    if len(event.get_plaintext().strip()) == 4 and (
            event.message_type == "private" or str(event.group_id) in get_driver().config.checkin_groups):
        return True
    return False

location = [30.3203028, 120.3372421]
register = on_command('login', rule=to_me(), priority=10, block=True)
code = on_regex('[0-9]{4}', rule=Rule(check), priority=10, block=True)
resp = None


async def check_result(route: Route):
    global resp
    response = await route.fetch()
    resp_dict = await response.json()
    resp_text = await response.text()
    if "msg" in resp_dict:
        resp = resp_dict["msg"]
    else:
        resp = "签到成功"
    logger.info(resp_text)


@register.handle()
async def handle(event: MessageEvent):
    if event.message_type == "group":
        await register.finish("Not support in QQ group, please use it in private msg")
    uid = event.get_user_id()
    async with async_playwright() as p:
        try:
            driver = await p.firefox.launch(headless=True)
            context = await driver.new_context()
            page = await context.new_page()
            await page.goto("https://skl.hdu.edu.cn/api/login/dingtalk/auth?index=&code=0&authCode=0&state=0")
            await page.wait_for_selector("div.module-qrcode-code", timeout=10000)
            await page.wait_for_timeout(1000)
            qrcode = await page.query_selector("div.module-qrcode-code")
            qrcode = await qrcode.screenshot()
            await register.send("Please finish it in 20 seconds by using dingding app\n" + MessageSegment.image(qrcode))
            await page.wait_for_selector("div.van-tabbar-item__text", timeout=45000)
            await page.goto("https://skl.hdu.edu.cn/api/login/dingtalk/auth?index=&code=0&authCode=0&state=0")
            if not path.exists("./dingding"):
                mkdir("./dingding")
            await context.storage_state(path=f"./dingding/{uid}.json")
            result = "Save cookies: Done"
        except TimeoutError:
            result = "Failed to save cookies: Timeout"
        except Exception as e:
            result = f"Failed to save cookies: {e}"
        finally:
            await context.close()
            await driver.close()
    await register.finish(result)


@code.handle()
async def handle(event: GroupMessageEvent):
    checkin_code = event.get_plaintext().strip()
    if len(checkin_code) != 4:
        return
    if not path.exists("./dingding"):
        return code.finish("Cookies not found")
    tasks = []
    for uid in listdir("./dingding"):
        uid = uid.split(".")[0]
        tasks.append(create_task(checkin(code, checkin_code, uid)))
    await gather(*tasks)


@code.handle()
async def handle(event: PrivateMessageEvent):
    checkin_code = event.get_plaintext().strip()
    if len(checkin_code) != 4:
        return
    uid = event.get_user_id()
    if not path.exists("./dingding") or not path.exists(f"./dingding/{uid}.json"):
        return code.finish("Cookies not found")
    await checkin(code, checkin_code, uid)


async def checkin(matcher: Type[Matcher], checkin_code: str, uid: str):
    global resp
    if not path.exists(f"./dingding"):
        return {"uid": uid, "status": False, "reason": "Cookie not found"}
    async with async_playwright() as p:
        try:
            driver = await p.firefox.launch(headless=True)
            context = await driver.new_context(
                screen=ViewportSize(width=480, height=720),
                geolocation=Geolocation(
                    latitude=location[0] + uniform(-0.0003, 0.0003),
                    longitude=location[1] + uniform(-0.0003, 0.0003),
                    accuracy=100
                ),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           " Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
                storage_state=f"./dingding/{uid}.json",
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});")
            await page.goto("https://skl.hdu.edu.cn/api/login/dingtalk/auth?index=&code=0&authCode=0&state=0")
            await page.wait_for_selector(".module-confirm-button", timeout=10000)
            confirm = await page.query_selector(".module-confirm-button")
            await confirm.click()
            await page.wait_for_selector("div.van-tabbar-item:nth-child(2)", timeout=10000)
            await page.goto("https://skl.hduhelp.com/#/sign/in")
            await page.wait_for_selector("div.van-password-input", timeout=10000)
            await page.route("https://skl.hdu.edu.cn/api/checkIn/code-check-in**", check_result)
            for num in checkin_code:
                if num == "0":
                    button = await page.query_selector("div.van-number-keyboard__keys > "
                                                       " div.van-key__wrapper.van-key__wrapper--wider > div")
                else:
                    button = await page.query_selector(f"div.van-number-keyboard__keys > div:nth-child({num}) > div")
                await button.click()
        except Exception as e:
            resp = e
        finally:
            await page.wait_for_timeout(500)
            await matcher.send(MessageSegment.at(user_id=uid) + str(resp))
            await context.close()
            await driver.close()

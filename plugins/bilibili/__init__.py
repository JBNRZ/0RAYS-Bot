import asyncio
import urllib.parse
from re import compile, findall

import lxml.html
from aiohttp import request, client
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent

analysis_stat = {}
analysis_bili = on_regex(
    "(b23.tv)|(www.bilibili.com/video)|(www.bilibili.com/bangumi)|(^(BV|bv)([0-9A-Za-z]{10}))|(^(av|AV)([0-9]+)("
    "/.*|\\?.*|)$)|(\\[\\[QQ小程序\\]哔哩哔哩\\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)", block=True)
headers = {
    'Referer': "https://www.bilibili.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "  Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
}


@analysis_bili.handle()
async def analysis_main(event: GroupMessageEvent):
    text = str(event.get_message()).strip()
    if "b23.tv" in text:
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    group_id = event.group_id
    msg = await bili_keyword(group_id, text)
    if msg:
        await analysis_bili.send(msg)


@analysis_bili.handle()
async def analysis_main(event: PrivateMessageEvent):
    text = str(event.get_message()).strip()
    if "b23.tv" in text:
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    group_id = 1
    msg = await bili_keyword(group_id, text)
    if msg:
        await analysis_bili.send(msg)


async def bili_keyword(group_id, text):
    try:
        # 提取url
        url = await extract(text)
        # 如果是小程序就去搜索标题
        if not url:
            pattern = compile(r'"desc":".*?"')
            desc = findall(pattern, text)
            i = 0
            while i < len(desc):
                title_dict = "{" + desc[i] + "}"
                title = eval(title_dict)
                vurl = await search_bili_by_title(title['desc'])
                if vurl:
                    url = await extract(vurl)
                    break
                i += 1

        # 获取视频详细信息
        if "www.bilibili.com/bangumi/play/" in url:
            msg = await bangumi_detail(url)
            vurl = url
        else:
            msg, vurl = await video_detail(url)

        # 避免多个机器人解析重复推送
        if group_id not in analysis_stat:
            analysis_stat[group_id] = vurl
            last_vurl = ""
        else:
            last_vurl = analysis_stat[group_id]
            analysis_stat[group_id] = vurl
        if last_vurl == vurl:
            return
    except Exception as e:
        msg = "Error: {}".format(type(e))
    return msg


async def b23_extract(text):
    b23 = compile(r'b23.tv\\/(\w+)').search(text)
    if not b23:
        b23 = compile(r'b23.tv/(\w+)').search(text)
    url = f'https://b23.tv/{b23[1]}'
    async with request('GET', url, headers=headers, timeout=client.ClientTimeout(10)) as resp:
        r = str(resp.url)
    return r


async def extract(text: str):
    try:
        aid = compile(r'(av|AV)\d+').search(text)
        bvid = compile(r'(BV|bv)([a-zA-Z0-9])+').search(text)
        epid = compile(r'ep\d+').search(text)
        ssid = compile(r'ss\d+').search(text)
        if bvid:
            url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
        elif aid:
            url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}'
        elif epid:
            url = f'https://www.bilibili.com/bangumi/play/{epid[0]}'
        else:
            url = f'https://www.bilibili.com/bangumi/play/{ssid[0]}'
        return url
    except IndexError:
        return None


async def search_bili_by_title(title: str):
    brackets_pattern = compile(r'[()\[\]{}（）【】]')
    title_without_brackets = brackets_pattern.sub(' ', title).strip()
    search_url = f'https://search.bilibili.com/video?keyword={urllib.parse.quote(title_without_brackets)}'

    try:
        async with request('GET', search_url, headers=headers, timeout=client.ClientTimeout(10)) as resp:
            text = await resp.text(encoding='utf8')
            content: lxml.html.HtmlElement = lxml.html.fromstring(text)
    except asyncio.TimeoutError:
        return None

    for video in content.xpath(
            '//li[@class="video-item matrix"]/a[@class="img-anchor"]'):
        if title == ''.join(video.xpath('./attribute::title')):
            url = ''.join(video.xpath('./attribute::href'))
            break
    else:
        url = None
    return url


async def video_detail(url):
    try:
        async with request('GET', url, headers=headers, timeout=client.ClientTimeout(10)) as resp:
            res = await resp.json()
            res = res['data']
        vurl = f"URL：https://www.bilibili.com/video/av{res['aid']}\n"
        title = f"标题：{res['title']}\n"
        up = f"UP主：{res['owner']['name']} (https://space.bilibili.com/{res['owner']['mid']})\n"
        desc = f"简介：{res['desc']}"
        msg = str(vurl) + str(title) + str(up) + str(desc)
        return msg, vurl
    except Exception as e:
        msg = "解析出错--Error: {}".format(type(e))
        return msg, None


async def bangumi_detail(url):
    try:
        async with request('GET', url, headers=headers, timeout=client.ClientTimeout(10)) as resp:
            res = await resp.text()
        content: lxml.html.HtmlElement = lxml.html.fromstring(res)
        name = content.xpath('//*[@id="media_module"]/div/a/text()')
        detail = content.xpath(
            '//*[@id="media_module"]/div/div[2]/a[1]/text()')
        pubinfo = content.xpath(
            '//*[@id="media_module"]/div/div[2]/span/text()')
        description = content.xpath(
            '//*[@id="media_module"]/div/div[3]/a/span[1]/text()')
        msg = f"URL：{url}\n标题：{name[0]}\n类型：{detail[0]}  {pubinfo[0]}\n简介：{description[0]}"
        return msg
    except Exception as e:
        msg = "解析出错--Error: {}".format(type(e))
        msg += f'\n{url}'
        return msg

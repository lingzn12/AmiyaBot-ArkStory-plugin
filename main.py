import os
from time import time

from amiyabot import Message, Chain

from core import GitAutomation, Admin
from core.customPluginInstance import AmiyaBotPluginInstance
from amiyabot.adapters.cqhttp import CQHTTPForwardMessage

from .tool.utils import HashTool
from .tool.logger import writeLog
from .story.chapter import chapter_story_search, chapter_story_search_result_list
from .tool.api import search_story, StorySearchParam
from .tool.constants import STORY_DATA
from .tool.cache import Cache

curr_dir = os.path.dirname(__file__)
obj = HashTool()
cache = Cache()
user = []

bot = AmiyaBotPluginInstance(
    name='熵的剧情查询插件',
    version='2.3',
    plugin_id='plot-plugin',
    plugin_type='story',
    description='明日方舟剧情查询插件，引用ArknightsSearch资源实现。',
    document=f'{curr_dir}/README.md',
    global_config_schema=f'{curr_dir}/config/config.json',
    global_config_default=f'{curr_dir}/config/default.json',
)


class Config:
    githubMirror: str = bot.get_config('githubMirror')
    updateStoryRes: str = bot.get_config('updateStoryRes')
    Page: int = bot.get_config('Page')
    PageWidth: int = bot.get_config('PageWidth')
    PageRender: int = bot.get_config('PageRender') * 1000
    maxTime: int = bot.get_config('maxTime')
    maxLevel: int = bot.get_config('maxLevel')
    memoryOptimize: bool = bot.get_config('memoryOptimize')


if Config.memoryOptimize:
    def advance_loading_list():
        Cache.set_cache(STORY_DATA, 'STORY_DATA')


    writeLog('初始化剧情缓存、哈希表中...')
    obj.story_list_hash()
    advance_loading_list()
    writeLog('初始化剧情缓存、哈希表成功')


async def update_resource(data: Message):
    if Config.updateStoryRes in data.text_original:
        if bool(Admin.get_or_none(account=data.user_id)):
            time1 = int(time())
            await data.send(Chain(data).text('开始更新剧情需要资源...'))
            git_path = 'resource/plugins/story'
            GitAutomation(git_path, Config.githubMirror).update()
            time2 = int(time())
            await data.send(Chain(data).text(f'更新完成,用时{str(time2 - time1)}秒。'))
    return False, 0


@bot.on_message(verify=update_resource, check_prefix=False, allow_direct=True, level=Config.maxLevel)
async def _(data: Message):
    pass


@bot.on_message(keywords='剧情查询', allow_direct=True, level=Config.maxLevel)
async def _(data: Message):
    search_content = data.text.split('剧情查询')[1]
    text_dict: dict = chapter_story_search_result_list(search_content, io_optimize=Config.memoryOptimize)

    result_list: list = []
    index_list: list = []

    for value in text_dict["result"]:
        index_list.append(value["index"])
        result_list.append(value["index"] + '：' + value["title"])

    page_text: dict = {
        "page": 1,
        "list": result_list
    }

    reply = await data.wait(
        Chain(data).html(f'{curr_dir}/template/islist.html', page_text, width=Config.PageWidth,
                         render_time=Config.PageRender),
        force=True, max_time=Config.maxTime)

    if reply.text is not None and reply.text in index_list:
        forward = CQHTTPForwardMessage(data)

        select_result: str = ''
        title: str = ''

        for value in text_dict["result"]:
            if value["index"] == reply.text:
                title = value["title"]
                select_result = str(value["title"]).split(' ')[0]
                break

        text_data: dict = chapter_story_search(reply.text, select_result, per_page_row=Config.Page - 1,
                                               io_optimize=Config.memoryOptimize)

        for text_index, text_value in text_data[select_result].items():
            page_text: dict = {
                "title": title,
                "page": int(text_index),
                "list": text_value["list"]
            }

            await forward.add_message(Chain(data).html(f'{curr_dir}/template/index.html', page_text,
                                                       width=Config.PageWidth,
                                                       render_time=Config.PageRender), user_id=data.instance.appid,
                                      nickname='兔兔')

        await forward.send()
        return Chain(reply).text(title)
    elif '退出' in reply.text:
        return Chain(reply).text('已退出')
    else:
        return Chain(reply).text('请输入正确索引')


@bot.on_message(keywords='筛选查询', allow_direct=True, level=Config.maxLevel)
async def _(data: Message):
    if data.user_id in user:
        return Chain(data).text('有在运行的任务，请完成后再重试')
    time1 = time()

    search_content = data.text_original.split(' ')

    if not search_content:
        return Chain(data).text('请按格式输入，检查是否缺少空格')

    del search_content[0]

    Type = {
        "文本": 'text',
        "干员": 'char',
        "活动": 'zone'
    }
    format_result_list: list = []

    for search_index in range(len(search_content)):
        search_value = search_content[search_index].split('-')
        if Type[search_value[0]]:
            value_tuple: StorySearchParam = StorySearchParam(type=Type[search_value[0]], param=search_value[1])
            format_result_list.append(value_tuple)
        else:
            return Chain(data).text('请按格式输入，检查选项是否输入错误')

    user.append(data.user_id)
    story_search: dict = search_story(format_result_list)
    total = story_search["total"] // 20 + 1
    forward = CQHTTPForwardMessage(data)

    for page_index in range(total):
        if data.text is not None and '退出' in data.text:
            for user_index in range(len(user)):
                if user[user_index] == data.user_id:
                    del user[user_index]
            return Chain(data).text('已退出')
        if page_index == 0:
            for page_text in story_search["list"]:
                await forward.add_message(Chain(data).text(page_text), user_id=data.instance.appid,
                                          nickname='兔兔')
        story_search_result: dict = search_story(format_result_list, offset=page_index * 20)

        for page_text in story_search_result["list"]:
            await forward.add_message(Chain(data).text(page_text), user_id=data.instance.appid,
                                      nickname='兔兔')

    await forward.send()
    for user_index in range(len(user)):
        if user[user_index] == data.user_id:
            del user[user_index]
    return Chain(data).text(f'搜索结果总数{total}条,用时{round(time() - time1, 3)}s')

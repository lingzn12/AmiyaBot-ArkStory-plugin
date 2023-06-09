import os

from amiyabot import Message, Chain
from core import GitAutomation, Admin
from .story.chapter import chapter_story_search, chapter_story_search_result_list
from core.customPluginInstance import AmiyaBotPluginInstance
from time import time
from amiyabot.adapters.cqhttp import CQHTTPForwardMessage

curr_dir = os.path.dirname(__file__)

bot = AmiyaBotPluginInstance(
    name='熵的剧情查询插件',
    version='2.2',
    plugin_id='plot-plugin',
    plugin_type='',
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


# if Config.updateStoryRes:
#     # story resource
#     resource_name_list: list = ['char_id2name.json', 'char_index.json', 'char_name2id.json', 'story_data.json',
#                                 'text_data.json', 'text_index.json', 'zone_index.json', 'zone_name.json']
#     for file_name in resource_name_list:
#         STORY_DATA = f'{Config.githubMirror}/{file_name}'
#         updateData([STORY_DATA], Config.githubMirror, Path(Path(curr_dir) / 'data' / 'story'))

async def update_resource(data: Message):
    if bool(Admin.get_or_none(account=data.user_id)) and Config.updateStoryRes in data.text_original:
        time1 = int(time())
        await data.send(Chain(data).text('开始更新剧情需要资源...'))
        git_path = 'resource/plugins/story'
        GitAutomation(git_path, Config.githubMirror).update()
        time2 = int(time())
        await data.send(Chain(data).text(f'更新完成,用时{str(time2 - time1)}秒。'))
    return False, 0


@bot.on_message(verify=update_resource, check_prefix=False, allow_direct=True)
async def _(data: Message):
    pass


@bot.on_message(keywords='剧情查询', allow_direct=True)
async def _(data: Message):
    search_content = data.text.split('剧情查询')[1]
    text_dict: dict = chapter_story_search_result_list(search_content)

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

    if reply.text in index_list:
        forward = CQHTTPForwardMessage(data)

        select_result: str = ''
        title: str = ''

        for value in text_dict["result"]:
            if value["index"] == reply.text:
                title = value["title"]
                select_result = str(value["title"]).split(' ')[0]
                break

        text_data: dict = chapter_story_search(reply.text, select_result, per_page_row=Config.Page - 1)

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

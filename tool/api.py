from typing import List, Literal, Dict
from pathlib import Path
from time import time
import requests
from pydantic import BaseModel

from .constants import SEARCH_STORY_URL, ARK_ALIAS_URL, ZONE_NAME
from .utils import read_json, HashTool


class StorySearchParam(BaseModel):
    """
    根据关键字搜索故事模型
    :StorySearchParam type: 搜索类型
    :StorySearchParam param: 搜索文本内容
    :StorySearchParam raw: 搜索参数
    """
    type: Literal['text', 'zone', 'char']
    param: str
    raw: str = None

    def __hash__(self):
        """
        返回StorySearchParam对象的哈希值
        """
        Hash: HashTool = HashTool()
        Hash.add(1, self.param)
        return Hash.get(1)


class SearchResult(BaseModel):
    """
    根据关键字搜索故事返回模型
    :SearchResult total: 搜索结果数
    :SearchResult page: 搜索文本页数
    :SearchResult offset: 当前位置
    :SearchResult search_time: 总用时
    :SearchResult list: 搜索条件文本列表
    """
    total: int
    page: int = None
    offset: int
    search_time: str
    list: List[str]


def story_api_format(result: dict, page_row: int, offset: int, total: int) -> Dict:
    listr = []

    zoneDict = {
        "Memory": '干员密录',
        "Main": '主线',
        "Rogue": '集成战略',
        "Activity": '活动'
    }
    result_text: str = ''

    for value in result["data"]:
        for data in value["data"]:
            raw: str = data["raw"]
            Type: str = data["type"]
            for data_text_list in data["data"]:
                cit = 0
                if Type == 'text':
                    for data_text_index in range(len(data_text_list)):
                        if cit == 1:
                            cit = 0
                            continue
                        if raw == data_text_list[data_text_index]:
                            result_text += f"{data_text_list[data_text_index - 1]}" \
                                           f"{data_text_list[data_text_index]}" \
                                           f"{data_text_list[data_text_index + 1]}\n"
                            cit = 1
                            continue
                        if data_text_index + 1 < len(data_text_list):
                            if raw == data_text_list[data_text_index + 1]:
                                continue
                        # result_text += f'{data_text_list[data_text_index]}\n'
                elif Type == 'char':
                    result_text += f"{data_text_list}\n"
        listr.append(f"{value['zone']}-{zoneDict[value['type']]}\n{value['name']}\n"
                     f"{result_text}")
        result_text = ''

    page = (len(listr) // page_row + 1) if page_row is not None else None
    return SearchResult(total=total, page=page, offset=offset, search_time='', list=listr).dict()


def search_story(params: List[StorySearchParam], lang: str = 'zh_CN', offset: int = 0,
                 page_row: int = None) -> Dict[str, List[list]]:
    time1 = time()
    """
    根据关键字搜索故事
    :param page_row: 每页故事列数
    :param params: 搜索条件列表
    :param lang: 故事的语言。默认为'zh_CN'
    :param offset: 搜索结果的偏移量。默认为0
    :return: 包含搜索结果的字典
    """
    params_list = []

    for p in params:
        alias = {
            "text": p.param,
            "type": 32767,
            "lang": 7,
            "output": 7,
            "mode": 1,
            "include_origin": False
        }
        result = requests.get(f'{ARK_ALIAS_URL}/alias/search', params=alias).json()

        if result:
            for name_index in result:
                params_list.append({"type": p.type, "param": p.param.replace(name_index[0], name_index[1]),
                                    "raw": p.raw})
        else:
            if p.type == 'zone':
                zone_name: dict = read_json(Path(ZONE_NAME))
                name: str = ''
                raw: str = ''
                for zone_name_index, zone_name_value in zone_name.items():
                    if p.param in zone_name_value["zh_CN"]:
                        name = zone_name_index
                        raw = zone_name_value["zh_CN"]
                        break

                params_list.append({"type": p.type, "param": name, "raw": raw})
            else:
                params_list.append({"type": p.type, "param": p.param, "raw": p.raw})

    param = {
        'params': params_list,
        'lang': lang,
        'offset': offset
    }
    result = requests.post(SEARCH_STORY_URL, json=param).json()

    if result:
        data = story_api_format(result, page_row, offset, result["total"])
        time2 = time()
        data.update({
            "search_time": f"{str(round(time2 - time1, 3))}s"
        })
        return data

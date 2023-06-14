from typing import Dict

from ..tool.cache import Cache
from ..tool.constants import STORY_DATA, TEXT_DATA

from ..tool.utils import read_json


def chapter_story_search(index: str, name: str, per_page_row: int = None, io_optimize: bool = False) -> Dict:
    data: dict = {
        name: {}
    }
    if io_optimize:
        from ..main import obj
        story_text_data = obj.get(index)
        text_list: list = str(story_text_data).split('\n')
    else:
        story_text_data = read_json(TEXT_DATA)["zh_CN"]
        text_list: list = str(story_text_data).split('\n')

    page_size = len(text_list) // per_page_row if per_page_row is not None else len(text_list)
    if page_size != 0:
        page_index: int = 1
        for i in range(0, len(text_list), page_size):
            data[name].update({
                str(page_index): {
                    "page": page_index,
                    "list": text_list[i:i + page_size]
                }
            })
            page_index += 1
    return data


def chapter_story_search_result_list(search_content: str, per_page_row: int = None, io_optimize: bool = False) -> Dict:
    story_dict: dict = {
        "result": []
    }

    if io_optimize:
        from ..main import obj
        story_text_data = Cache().get_cache(STORY_DATA)
    else:
        story_text_data = read_json(STORY_DATA)

    for index, value in story_text_data.items():
        name: str = value["name"]["zh_CN"]
        zone: str = value["zone"]
        if search_content in name:
            if per_page_row is not None:
                for page in range(per_page_row):
                    story_dict["result"].append({
                        "page": per_page_row
                    })

            story_dict["result"].append({
                "index": index,
                "title": zone + ' ' + name
            })
    return story_dict

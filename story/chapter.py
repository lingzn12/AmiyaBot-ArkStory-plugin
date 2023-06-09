from typing import Dict

from ..tool.constants import STORY_DATA, TEXT_DATA
from ..tool.utils import read_json


def chapter_story_search(index: str, name: str, per_page_row: int = None) -> Dict:
    data: dict = {
        name: {}
    }
    file_data = read_json(TEXT_DATA)["zh_CN"]
    text_text_list: list = str(file_data[index]).split('\n')

    page_size = len(text_text_list) // per_page_row if per_page_row is not None else len(text_text_list)
    if page_size != 0:
        page_index: int = 1
        for i in range(0, len(text_text_list), page_size):
            data[name].update({
                str(page_index): {
                    "page": page_index,
                    "list": text_text_list[i:i + page_size]
                }
            })
            page_index += 1

    return data


def chapter_story_search_result_list(search_content: str, per_page_row: int = None) -> Dict:
    story_dict: dict = {
        "result": []
    }
    file_data = read_json(STORY_DATA)

    for index, value in file_data.items():
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

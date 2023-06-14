import json

from pathlib import Path
from typing import List, Dict
import hashlib

from .constants import TEXT_DATA


class StoryData:
    story_list: dict = {}


class HashTool:
    def __init__(self):
        self.hash_table = {}

    def add(self, key, value):
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        self.hash_table[hash_key] = value

    def get(self, key):
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.hash_table.get(hash_key)

    def update(self, key, value):
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        if hash_key in self.hash_table:
            self.hash_table[hash_key] = value

    def remove(self, key):
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        if hash_key in self.hash_table:
            del self.hash_table[hash_key]

    def story_list_hash(self):
        text_data: dict = read_json(TEXT_DATA)

        for text_data_index, text_data_value in text_data['zh_CN'].items():
            self.add(text_data_index, text_data_value)


def read_txt(filepath: Path, encoding: str = 'utf_8_sig') -> str:
    with filepath.open(mode="r", encoding=encoding) as file:
        content = file.read()
        return content


def read_json(filepath: Path, encoding: str = 'utf_8_sig') -> Dict:
    with filepath.open(mode="r", encoding=encoding) as file:
        return json.load(file)


def write_json(data: dict, filepath: Path, encoding: str = 'utf-8') -> None:
    with filepath.open('w', encoding=encoding) as f:
        json.dump(data, f, sort_keys=False, indent=4, ensure_ascii=False)


# def download_json(url: str, filepath: Path):
#     resp = requests.get(url, stream=True)
#
#     with filepath.open('wb') as file, tqdm(
#         desc=filepath.stem,
#         total=int(resp.headers.get('Content-Length', 0)),
#         unit='B',
#         unit_scale=True,
#         unit_divisor=1024
#     ) as bar:
#         for data in resp.iter_content(chunk_size=1024):
#             size = file.write(data)
#             bar.update(size)
#         bar.close()


# def stage_table_data() -> Dict:
#     stage_table = read_json(STAGE_TABLE)
#     for stageValue in stage_table["stages"].values():
#         StoryData.story_list.update({
#             stageValue["stageId"]: {
#                 "stageId": stageValue["stageId"],
#                 "name": stageValue["name"],
#                 "levelId": stageValue["levelId"]
#             }
#         })
#     return StoryData.story_list


def file_list_handle(path, sub_dir=False, suffix_list=None) -> List:
    '''
        tool：输入路径，支持文件路径和文件夹路径
        sub_dir：当为True时含子目录，为False时不含子目录
        suffix_list：文件类型列表，按要求的列出全部符合条件的文件，为空时列出全部文件，如：[".xlsx",".xls"]
    '''

    if suffix_list is None:
        suffix_list = ['.txt']
    file_list = []
    if not suffix_list:
        if sub_dir:
            [suffix_list.append(Path(f).suffix) for f in Path(path).glob(f"**\*.*") if Path(f).is_file()]
        else:
            [suffix_list.append(Path(f).suffix) for f in Path(path).glob(f"*.*") if Path(f).is_file()]
        suffix_list = list(set(suffix_list))
    # [print(i) for i in suffix_list]
    if Path(path).exists():
        # 目标为文件夹
        if Path(path).is_dir():
            if sub_dir:
                for i in suffix_list:
                    [file_list.append({"tool": str(f), "file_name": f.stem}) for f in Path(path).rglob(f"**\*{i}")]
            else:
                [file_list.append(str(f)) for f in Path(path).iterdir() if Path(f).is_file and f.suffix in suffix_list]
        elif Path(path).is_file():
            file_list = [path]

        # 去除临时文件
        file_list_temp = []  # {"tool": str(Path(HANDBOOK_INFO_TABLE)), "file_name": Path(HANDBOOK_INFO_TABLE).stem}
        for y in file_list:
            if "~$" in y["tool"]:
                continue
            file_list_temp.append(y)
        return file_list_temp
    else:
        print("输入有误！")
        return []

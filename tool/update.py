import json
import os
import requests

from pathlib import Path

from .cache import CacheTow
from .logger import writeLog
from .utils import write_json


def updateData(url: list, gitImageUrl: str, path: Path, use_local: bool = False):
    BASE_URL_LIST = [
        (gitImageUrl, Path(path))
    ]

    localPath: list = []

    for index in BASE_URL_LIST:
        for url_index in range(len(url)):
            if index[0] in url[url_index]:
                if not os.path.isdir(index[1]):
                    os.makedirs(index[1])
                localPath.append(str(Path(url[url_index].replace(index[0], str(index[1])))))

    if not os.path.isdir(Path(path)):
        os.makedirs(Path(path))

    if use_local:
        try:
            cache_data = CacheTow()
            data = cache_data.get_cache(Path(localPath[0]))
            return data

        except json.decoder.JSONDecodeError:
            return writeLog(f'\033[1;31mCould not load file "{os.path.basename(localPath[0])}"\033[0;0m', "error")

        except IOError:
            return writeLog(f'\033[1;31mCould not open file "{os.path.basename(localPath[0])}"\033[0;0m', "error")

    for index in range(len(localPath)):
        try:
            resp = requests.get(url[index]).json()

            write_json(resp, Path(localPath[index]))
            writeLog(
                f'Auto-update {"github" if "gitee" not in url else "gitee"} of file "{os.path.basename(localPath[index])}" - '
                '\033[1;32mSuccessful!\033[0;0m',
                "info")
        except requests.exceptions.RequestException:
            if not os.path.exists(localPath[index]):
                return writeLog(
                    f'\033[1;31m下载文件"{os.path.basename(localPath[index])}"失败，请更换镜像或网络环境重试\033[0;0m',
                    "error")

    return None

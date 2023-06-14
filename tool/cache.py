import os
from functools import lru_cache
from pathlib import Path
from time import time
from typing import Optional, Dict

from .utils import read_json
from .constants import STORY_DATA


class Cache:
    cached_data: Dict = dict()
    cache_time: int = 600

    @classmethod
    @lru_cache(maxsize=None)
    def get_cache(cls, local_path: str) -> Optional[dict]:
        # 获取数据名称
        data_name = os.path.splitext(os.path.basename(local_path))[0]
        # 如果数据名称已经在缓存中，则判断数据是否过期
        if data_name in cls.cached_data:
            current_modification_time = os.path.getmtime(local_path)
            if current_modification_time <= cls.cached_data[data_name]['modification_time']:
                # 如果数据未过期，则返回缓存中的数据
                return cls.cached_data[data_name]['data']
        # 如果数据未被缓存或已过期，则重新设置缓存
        return cls.set_cache(local_path, data_name)

    @classmethod
    def set_cache(cls, local_path: str, data_name: str) -> Optional[dict]:
        # 读取数据
        data = read_json(Path(local_path), encoding='utf-8')
        # 设置过期时间
        modification_time = int(time()) + cls.cache_time
        # 将数据存储到缓存中
        cls.cached_data[data_name] = {'data': data, 'modification_time': modification_time}
        # 返回缓存中的数据
        return cls.cached_data[data_name]['data']

import os

from pathlib import Path

PATH = Path.cwd()
RELATIVE_PATH = Path(os.path.dirname(__file__)).parent

# other api
SEARCH_STORY_URL = 'https://search.arkfans.top/api/story'
ARK_ALIAS_URL = 'https://alias.arkfans.top'

# story resource
STORY_RESOURCE = PATH / 'resource' / 'plugins' / 'story' / 'data' / 'story'
STORY_DATA = STORY_RESOURCE / 'story_data.json'
TEXT_DATA = STORY_RESOURCE / 'text_data.json'
ZONE_NAME = STORY_RESOURCE / 'zone_name.json'

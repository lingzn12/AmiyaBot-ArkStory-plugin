import os

from pathlib import Path

PATH = Path.cwd()
RELATIVE_PATH = Path(os.path.dirname(__file__)).parent

# gamedata tool
GAMEDATA = PATH / 'resource' / 'gamedata' / 'gamedata'

# story
STORY_OBT = GAMEDATA / 'story' / 'obt'

# excel
EXCEL = GAMEDATA / 'excel'
HANDBOOK_INFO_TABLE = EXCEL / 'handbook_info_table.json'
STAGE_TABLE = EXCEL / 'stage_table.json'
ACTIVITY_TABLE = EXCEL / 'activity_table.json'

# other
SEARCH_STORY_URL = 'https://search.arkfans.top/api/story'

# story resource
STORY_RESOURCE = PATH / 'resource' / 'plugins' / 'story' / 'data' / 'story'
STORY_DATA = STORY_RESOURCE / 'story_data.json'
TEXT_DATA = STORY_RESOURCE / 'text_data.json'

import os.path
from pathlib import Path

from split_settings.tools import optional, include

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENVVAR_SETTINGS_PREFIX = "PICBUDGET_SETTING_"
LOCAL_SETTINGS_PATH = os.getenv(f"{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH")


if not LOCAL_SETTINGS_PATH:
    LOCAL_SETTINGS_PATH = "local/settings.dev.py"

if not os.path.isabs(LOCAL_SETTINGS_PATH):
    LOCAL_SETTINGS_PATH = str(BASE_DIR / LOCAL_SETTINGS_PATH)

# yapf: disable
include(
    'base.py',
    'logging.py',
    'channels.py',
    'custom.py',
    'celery.py',
    'rest_framework.py',
    optional(LOCAL_SETTINGS_PATH),
    'envvars.py',
    'docker.py',
)

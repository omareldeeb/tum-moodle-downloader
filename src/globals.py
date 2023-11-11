from pathlib import Path

# Build paths relative to absolute path of script (or rather the scripts parent dir)
# Source: https://stackoverflow.com/a/55051039
BASE_PATH = Path(__file__).parent
CREDENTIALS_PATH = (BASE_PATH / "../credentials.json").resolve()
COURSE_CONFIG_PATH = (BASE_PATH / "../course_config.json").resolve()
DOWNLOAD_CONFIG_PATH = (BASE_PATH / "../download_config.json").resolve()

global_session = None


def set_global_session(session):
    global global_session
    global_session = session


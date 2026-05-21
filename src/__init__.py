import logging.config
import shutil
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent.resolve()
LOGGING_FILE = (ROOT_FOLDER / "logging.conf").resolve()
TEMPLATE_LOGGING_FILE = (ROOT_FOLDER / "template_logging.conf").resolve()

if not LOGGING_FILE.exists():
    shutil.copy(TEMPLATE_LOGGING_FILE, LOGGING_FILE)

logging.config.fileConfig(LOGGING_FILE)

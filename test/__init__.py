import logging.config
from pathlib import Path

RESOURCES_FOLDER = (Path(__file__).parent / Path("resources")).resolve()
ROOT_FOLDER = Path(__file__).parent.parent.resolve()

logging.config.fileConfig(ROOT_FOLDER / "logging.conf")

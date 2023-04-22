import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format=(
        "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
    ),
    level=logging.DEBUG if '--debug' in sys.argv else logging.INFO,
)

PROJECT_PATH = Path(__name__).parent.resolve()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_DEVELOPER_ID = int(os.environ["TELEGRAM_DEVELOPER_ID"])
TELEGRAM_MANAGER_ID = int(os.environ["TELEGRAM_MANAGER_ID"])

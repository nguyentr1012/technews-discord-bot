import sys
import os

# Thêm thư mục gốc vào sys.path để tránh lỗi ModuleNotFoundError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)

from src.bot.discord_bot import start

if __name__ == "__main__":
    start()

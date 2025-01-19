import logging
from logging.handlers import RotatingFileHandler
import os
from enum import Enum

class ScriptIdentifier(Enum):
    SUMMARIZER = "AI_SUMMARIZER"
    DATABASE = "DATABASE_MANAGER"
    OUTLINER = "AI_OUTLINER"
    CHAPTER = "AI_CHAPTER_MAKER"
    AGENTSUMMARIZER = "AI_AGENT_SUMMARIZER"
    MAIN = "POKOSCRIBE"
    AHSS = "AHSS_SEARCH_TOOL"
    SCIHUB = "SCIHUB_DOWNLOADER"

class PokoLogger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PokoLogger, cls).__new__(cls)
            cls._setup_logger()
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    @classmethod
    def _setup_logger(cls):
        try:
            os.makedirs('logs', exist_ok=True)
            cls._logger = logging.getLogger('PokoScribe')
            cls._logger.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s - [%(script_id)s] - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Main log handler
            main_handler = RotatingFileHandler(
                'logs/pokoscribe.log',
                maxBytes=10000000,
                backupCount=5
            )
            main_handler.setFormatter(formatter)
            cls._logger.addHandler(main_handler)

            # Error log handler
            error_handler = RotatingFileHandler(
                'logs/pokoscribe_errors.log',
                maxBytes=10000000,
                backupCount=5
            )
            error_handler.setFormatter(formatter)
            error_handler.setLevel(logging.WARNING)
            cls._logger.addHandler(error_handler)
        except Exception as e:
            print(f"Failed to setup logger: {e}")
            raise

    def _log(self, level, script_id, message):
        if not self._logger:
            self._setup_logger()
        extra = {'script_id': script_id}
        self._logger.log(level, message, extra=extra)

    def info(self, script_id: ScriptIdentifier, message: str):
        self._log(logging.INFO, script_id.value, message)

    def error(self, script_id: ScriptIdentifier, message: str):
        self._log(logging.ERROR, script_id.value, message)

    def warning(self, script_id: ScriptIdentifier, message: str):
        self._log(logging.WARNING, script_id.value, message)

    def debug(self, script_id: ScriptIdentifier, message: str):
        self._log(logging.DEBUG, script_id.value, message)
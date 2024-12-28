# ai_z_logsconfig.py

import logging
import os
from typing import Dict, Any

def get_log_config(
    log_name: str = 'PDFSummarizer',
    log_dir: str = 'logs',
    main_log: str = 'event.log',
    error_log: str = 'error.log'
) -> Dict[str, Any]:
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'file_formatter': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'console_formatter': {
                'format': '%(levelname)s: %(message)s'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_dir, main_log),
                'formatter': 'file_formatter',
                'level': 'INFO'
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_dir, error_log),
                'formatter': 'file_formatter',
                'level': 'ERROR'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formatter',
                'level': 'DEBUG'
            }
        },
        'loggers': {
            log_name: {
                'handlers': ['file', 'error_file', 'console'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }

def setup_logging(config: Dict[str, Any]) -> None:
    os.makedirs(config['handlers']['file']['filename'].rsplit('\\', 1)[0], exist_ok=True)
    logging.config.dictConfig(config)
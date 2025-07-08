import logging
from logging.config import dictConfig

from utils.path import LOG_DIR

# 로깅 설정
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "formatter": "default",
        },
        "db_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "db.log",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console", "app_file"],
        "level": "INFO",
    },
    "loggers": {
        "sqlalchemy.engine": {
            "handlers": ["db_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)


# 로거 인스턴스 반환
def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)


# 기본 로거 인스턴스 (main.py에서 사용)
main_logger = get_logger("app.main")

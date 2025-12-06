"""
统一日志配置
提供结构化的日志管理
"""

from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 确保日志目录存在
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        # 控制台输出
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        # 文件输出 - 所有日志
        "file_all": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "all.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        # 文件输出 - API 服务
        "file_api": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "api.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        # 文件输出 - 错误日志
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        # 文件输出 - AI 服务
        "file_ai": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "ai.log",
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        # 文件输出 - OCR 服务
        "file_ocr": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "ocr.log",
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        # 文件输出 - 搜索服务
        "file_search": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "search.log",
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        # Django 核心日志
        "django": {
            "handlers": ["console", "file_all"],
            "level": "INFO",
            "propagate": False,
        },
        # Django 请求日志
        "django.request": {
            "handlers": ["console", "file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        # API 视图日志
        "api.views": {
            "handlers": ["console", "file_api"],
            "level": "INFO",
            "propagate": False,
        },
        # AI 服务日志
        "api.services.ai_service": {
            "handlers": ["console", "file_ai", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        # OCR 服务日志
        "api.services.ocr_service": {
            "handlers": ["console", "file_ocr", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        # 搜索服务日志
        "api.services.search_service": {
            "handlers": ["console", "file_search", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        # 通用 API 日志
        "api": {
            "handlers": ["console", "file_api", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file_all"],
        "level": "INFO",
    },
}


def get_logger(name: str):
    """
    获取指定名称的日志器

    使用示例:
        from config.logging import get_logger
        logger = get_logger(__name__)
        logger.info("This is a log message")
    """
    import logging

    return logging.getLogger(name)

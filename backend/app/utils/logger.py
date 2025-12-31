import logging
from logging import Logger, StreamHandler

from logtail import LogtailHandler

from app.config.settings import settings


def setup_logging() -> None:
    handler: StreamHandler = StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s| %(name)s:%(funcName)s:%(lineno)s - %(message)s",
            datefmt="%d-%M-%Y %I:%M:%S %p",
        )
    )
    root: Logger = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root.handlers.clear()
    if settings.DEBUG:
        root.addHandler(handler)

    # integrate betterstack
    logtail_handler: LogtailHandler = LogtailHandler(
        source_token=settings.BETTER_STACK_SOURCE_TOKEN,
        host=settings.BETTER_STACK_INGESTING_HOST,
    )
    if not settings.DEBUG:
        root.addHandler(logtail_handler)

    # clear handlers of uvicorn
    for lg in ["uvicorn", "uvicorn.access", "watchfiles"]:
        uvicorn_logger: Logger = logging.getLogger(lg)
        uvicorn_logger.handlers.clear()
        if settings.DEBUG:
            uvicorn_logger.addHandler(handler)
        else:
            uvicorn_logger.addHandler(logtail_handler)

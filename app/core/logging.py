import logging
import logtail
from app.config import logging_settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("fastship")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console_handler)


    logtail_handler = logtail.LogtailHandler(
            source_token=logging_settings.LOGTAIL_SOURCE_TOKEN,
            host=logging_settings.LOGTAIL_HOST,
        )
    logtail_handler.setFormatter(
            logging.Formatter("[%(levelname)s]: %(message)s")
        )
    logger.addHandler(logtail_handler)

    return logger


logger = setup_logging()
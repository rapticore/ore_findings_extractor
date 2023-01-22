import logging
import os
import sys
from inspect import getframeinfo as fi, currentframe as cf, currentframe
from pprint import pformat

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from src.constants.discovery_constants import SOCKET_LISTENER, LOG_TIME


levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']


def get_logger(filename: str):
    level = os.environ.get('LOG_LEVEL', 'DEBUG')
    if level not in levels:
        level = 'DEBUG'

    ch = logging.StreamHandler(sys.stdout)
    # create formatter
    if LOG_TIME or SOCKET_LISTENER:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s \r')
    else:
        formatter = logging.Formatter('%(levelname)s - %(message)s \r')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logging.basicConfig(force=True, handlers=[ch])

    logging.getLogger().setLevel(level)

    [logging.getLogger(p).setLevel(logging.ERROR) for p in ["boto3", "botocore", "redis", "kubernetes"]]

    urllib3.disable_warnings(InsecureRequestWarning)
    disable_loggers = ["urllib3", "requests"]
    for dl in disable_loggers:
        logging.getLogger(dl).setLevel("CRITICAL")
    custom_logger = logging.getLogger(filename)
    custom_logger.setLevel(level)
    return custom_logger


logger = get_logger(__name__)


def oneline_frame_info(text: str = None, frame=None):
    frame = frame if frame else fi(cf().f_back)
    file = "/".join(frame.filename.split("/")[-2:])
    _text = text + " " if text else ""
    return f"[{file}:{frame.lineno}.{frame.function}()]{_text}"


def log_frame_warning(_logger: logging.Logger, message: str = None, frame=None, **kwargs):
    log_frame(_logger, logging.WARNING, message, frame=frame, **kwargs)


def log_frame_info(_logger: logging.Logger, message: str = None, **kwargs):
    log_frame(_logger, logging.INFO, message, **kwargs)


def log_frame_debug(_logger: logging.Logger, message: str = None, **kwargs):
    log_frame(_logger, logging.DEBUG, message, **kwargs)


def log_frame_error(_logger: logging.Logger, message: str = None, **kwargs):
    log_frame(_logger, logging.ERROR, message, **kwargs)


def log_frame(_logger: logging.Logger, level, message: str = None, frame=None, **kwargs):
    text_kwargs = [f"{k}:{v}" for k, v in kwargs.items()]
    if frame is None:
        frame = fi(currentframe().f_back.f_back)
    _message = f" {message} " if message else ""
    _text_kwargs = f" {text_kwargs} " if text_kwargs else ""
    _logger.log(level, msg=f"{oneline_frame_info(frame=frame)}{_message}{_text_kwargs}")


def oneline_exc_info(extra: dict = None):
    """Gets a one-line Exception Info string for logging"""
    ex, tb = sys.exc_info()[-2:]
    frame = fi(tb)
    file = "/".join(frame.filename.split("/")[-2:])
    pprint_extra = f" {pformat(extra)}" if extra else ""
    return f"[{file}:{frame.lineno}.{frame.function}()] {{{type(ex).__name__}}} {ex}{pprint_extra}"


def print_oneline_exc_info():
    print(oneline_exc_info())


def main():
    """Test it"""
    try:
        raise RuntimeError("A wild foo is on the loose! Get to the Bar and grab the Baz!")
    except RuntimeError as e:
        print(oneline_exc_info())
        pass


if __name__ == "__main__":
    main()

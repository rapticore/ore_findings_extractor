import datetime
import sys
from decimal import Decimal
from inspect import getframeinfo as fi, currentframe

import botocore.config
from botocore.exceptions import ClientError

from src.helpers.logging_helper import oneline_exc_info, get_logger, log_frame_warning, log_frame_error

logger = get_logger(__name__)


def exception_handler(e: Exception, do_exit=False, args=None):

    if isinstance(e, KeyboardInterrupt):
        logger.warning(oneline_exc_info())
        return
    warning_exceptions = {
        'UnrecognizedClientException', 'InvalidClientTokenId', 'ValidationError', 'ResourceNotFoundException',
        'NoSuchPublicAccessBlockConfiguration', 'NoSuchBucketPolicy', 'AccessDenied', 'RegionDisabledException',
        'RepositoryPolicyNotFoundException', 'NoSuchTagSet', 'ScanNotFoundException'
    }
    if isinstance(e, ClientError):
        if e.response['Error']['Code'] in warning_exceptions:
            log_frame_warning(logger, frame=fi(currentframe().f_back), args=args,
                              ERROR=f"{e.response['Error']['Code']}: {e.response['Error']['Message']}")
            return

    log_frame_error(logger, frame=fi(currentframe().f_back), args=args, ERROR=e)
    logger.exception(e)
    if do_exit:
        sys.exit(1)


def datetime_handler(input_date):
    if isinstance(input_date, datetime.datetime):
        return input_date.isoformat()
    if isinstance(input_date, bytes):
        log_frame_warning(logger, f'Converting a bytes type object into string, object: {input_date}')
        return input_date.decode("utf-8")
    raise TypeError(f"Unknown type, input: {input_date}, type: {type(input_date)}")



def remove_duplicates(dirty_list):
    clean_list = []
    [clean_list.append(x) for x in dirty_list if x and x not in clean_list]
    return clean_list


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

    if isinstance(obj, bytes):
        log_frame_warning(logger, f'Converting a bytes type object into string, object: {obj}')
        return obj.decode("utf-8")

    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)


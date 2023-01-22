import os
from os import environ

from src.helpers import helper_load_env

helper_load_env.load()

DEFAULT_ENV_NAME = "local-development"
DEFAULT_GROUP = "Default"
# Botocore client settings
BOTOCORE_MAX_RETRIES = int(environ.get("BOTOCORE_MAX_RETRIES", "10"))
BOTOCORE_MAX_POOL_CONNECTIONS = int(environ.get("BOTOCORE_MAX_POOL_CONNECTIONS", "50"))
# Default session name for botocore client sessions
DEFAULT_SESSION_NAME = "support@rapticore.com"

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
TENANT_ID = os.getenv("ENV_NAME")
# if ENV_NAME is not defined in OS Environment, set it
if TENANT_ID is None:
    TENANT_ID = DEFAULT_ENV_NAME
SOCKET_LISTENER = os.environ.get("SOCKET_LISTENER", "False") == "False"
LOG_TIME = os.environ.get("LOG_TIME", "False") == "True"
API_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT")
REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
GRAPHQL_PRODUCTION_ENDPOINT = "https://api-svc.rapticore.internal/graphql"
AWS_JOB_POLLING_INTERVAL = float(os.environ.get("AWS_JOB_POLLING_INTERVAL", "2"))
PAGE_SIZE = int(os.environ.get("PAGE_SIZE", "1000"))
PAGE_SIZE_SMALL = int(os.environ.get("PAGE_SIZE_SMALL", "20"))
MAX_OFFENDERS = int(os.environ.get("MAX_OFFENDERS", "1000"))
GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", GRAPHQL_PRODUCTION_ENDPOINT)

from src.constants.discovery_constants import PAGE_SIZE
from src.graphql import helper_graphql_queries
from src.helpers.handlers import exception_handler, default
from src.helpers.logging_helper import log_frame_debug, get_logger, log_frame_error

logger = get_logger(__name__)



def execute_customer_paginated_list_query(query, url, auth, data_key, where_condition=None, page_size=PAGE_SIZE, sort_criteria=None):
    log_frame_debug(logger, data_key=data_key, where_condition=where_condition)
    total_list = []
    variables = {}
    try:
        skip = 0
        if where_condition:
            variables['whereCondition'] = where_condition
        if sort_criteria:
            variables['sortCriteria'] = sort_criteria
        while True:
            variables.update(dict(take=page_size, skip=skip))
            response = helper_graphql_queries.execute_customer_query(query,url, auth, variables)
            total_list.extend(response.get("data", {}).get(data_key, {}).get("items", []))
            skip = skip + page_size
            records_count = len(response.get("data", {}).get(data_key, {}).get("items", []))
            if records_count < page_size:
                break
    except Exception as e:
        exception_handler(e, args=variables)
    return total_list

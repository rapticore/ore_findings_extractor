
from src.constants.service_names import ServiceNames
from src.graphql import helper_graphql_queries, common_functions
from src.graphql.common_functions import execute_customer_paginated_list_query
from src.helpers.logging_helper import log_frame_debug, get_logger

logger = get_logger(__name__)


def get_resources_by_type(service_name, url, auth, account, resource_type=None, resource_type_operator="eq", custom_filter=None):
    log_frame_debug(logger)
    where_condition = {"propertyName": "assetStatus", "ne": "Archived", "and": [
        {"propertyName": "service", "eq": service_name},
    ]}
    if account:
        account_filter = {"propertyName": "account", "eq": account}
        where_condition.get("and").append(account_filter)
    if resource_type is not None:
        condition = {"propertyName": "resourceType", resource_type_operator: resource_type}
        where_condition.get("and").append(condition)
    if custom_filter:
        where_condition.get("and").append(custom_filter)
    return execute_customer_paginated_list_query(helper_graphql_queries.list_resources_query, url, auth,'listResources',
                                        where_condition)


def get_ec2_instances(account, url, auth):
    return get_resources_by_type(ServiceNames.Aws.EC2, url, auth, account, resource_type="instance")



def get_ecr_repositories(account):
    return get_resources_by_type(ServiceNames.Aws.ECR, account, resource_type="repository")

def get_ec2_instances_customer(account, url, auth):
    return get_resources_by_type(ServiceNames.Aws.EC2, url, auth, account, resource_type="repository")



def get_ecs_containers(account=None):
    return get_resources_by_type(ServiceNames.Aws.ECS, account, resource_type="container")

def get_ecs_containers_count(url, auth, account=None):
    return get_resources_by_type(ServiceNames.Aws.ECS, url, auth, account, resource_type="container")


def get_k8s_pods(account=None):
    return get_resources_by_type(ServiceNames.Aws.EKS, account, resource_type="pod")


def get_running_ecs_container_images(account=None):
    images = set()
    containers = get_ecs_containers(account)
    for container in containers:
        container_data_list = container['resourceData']
        for container_data in container_data_list:
            for container_definition in container_data.get('containerDefinitions', []):
                images.add(container_definition['image'])

    return list(images)


def get_running_k8s_pod_images(account=None):
    images = set()
    pods = get_k8s_pods(account)
    for pod in pods:
        pod_data = pod['resourceData']
        for container_definition in pod_data.get('spec', None).get('containers', []):
            images.add(container_definition['image'])

    return list(images)

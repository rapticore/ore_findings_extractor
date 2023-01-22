import logging

import requests

from src.constants.discovery_constants import GRAPHQL_ENDPOINT
from src.helpers import helper_load_env
from src.helpers.logging_helper import get_logger

helper_load_env.load()

logger = get_logger(__name__)

list_cloud_accounts_query = """
    query listCloudAccounts ($whereCondition: WhereConditionInput, $sortCriteria: SortCriteriaInput){
        listCloudAccounts (input: { whereCondition: $whereCondition, sortCriteria: $sortCriteria }){
          items {
            id
            displayName
            accountType
            awsRoleArn
            awsRoleExternalId
            awsAccountId
            status
            defaultRegions
            applicationCreationTags
            environmentType
            cloudAccountGroupId
          }
        }
      }
"""

list_resources_query = """
query listResources(
    $skip: NonNegativeInt
    $take: NonNegativeInt
    $whereCondition: WhereConditionInput
  ) {
    listResources(
      input: {
        skip: $skip
        take: $take
        whereCondition: $whereCondition
      }
    )
    {
    items {
      id
      displayName
      description
      organizationId
      updated
      created
      version
      service
      urn
      cloudType
      account
      region
      resourceType
      resourceData
      s3key
      resourceID
      dateLastSeen
      assetStatus
      hostname
      dn
      # publicStatus
      vulnerabilities{
      count
        items{
          id
          severity
          firstReported
          lastReported
          sources
        }
      }
      iamRoleArn
      tags
      metadata
      sourceData
      severity
      riskLevel
    }
  }
}
"""

def execute_customer_query(query, url, authorization, variables=None):
    if variables is None:
        variables = []
    GRAPHQL_ENDPOINT = url
    origin_string = f"'Origin : {url}'"
    headers = {"content-type": "application/json", "authorization": authorization}
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT, json={"query": query, "variables": variables}, headers=headers, verify=False,
        )
        if response.status_code == 200 and response.json().get('errors') is None:
            data = response.json()
            if not data and not data.get("data"):
                logging.warning("WARNING: Request did not return any data!")
            return data
        else:
            logger.error(f"Error posting json :: 'query': {query}, 'variables': {variables}")
            raise Exception(f"Query failed to run by returning error {response.json().get('errors')[0]['message']} ")

    except Exception as e:
        raise Exception(e)

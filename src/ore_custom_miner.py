import json
import sys

import pandas as pd
from dateutil.parser import parse
from nested_lookup import nested_lookup

from src.graphql import helper_graphql_queries
from src.graphql import resource_customer_graphql
from src.helpers.handlers import exception_handler
from src.helpers.logging_helper import log_frame_debug, get_logger, log_frame_info

logger = get_logger(__name__)
url = None
auth = None


def get_cloud_details():
    try:
        log_frame_debug(logger)
        result = helper_graphql_queries.execute_customer_query(helper_graphql_queries.list_cloud_accounts_query, url,
                                                               auth)
        cloud_details = result.get("data").get("listCloudAccounts").get('items')
        cloud_list = []
        for acct in cloud_details:
            acc_dictionary = dict(displayName=acct.get('displayName'), environment=acct.get('environmentType'),
                                  awsAccountId=acct.get('awsAccountId'))
            cloud_list.append(acc_dictionary)
        return cloud_list
    except Exception as e:
        exception_handler(e)


def ecs_count_account(cloud_list):
    log_frame_info(logger)
    try:
        ecs_count_accounts = []
        for accounts in cloud_list:
            account = accounts.get("awsAccountId")
            count = resource_customer_graphql.get_ecs_containers_count(url, auth, account)
            ecs_count = dict(awsAccountId=accounts.get('awsAccountId'), ecs=count)
            ecs_count_accounts.append(ecs_count)
        return ecs_count_accounts
    except Exception as e:
        exception_handler(e)


def cloud_name_lookup(account, cloud_list):
    for cloud in cloud_list:
        try:
            if account == cloud.get('awsAccountId'):
                return cloud
        except Exception as e:
            print(e)


def exel_writer(ec2_data, ecr_data):
    log_frame_debug(logger)
    try:
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        file = 'stats_multiple.xlsx'

        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        df1 = pd.DataFrame(ec2_data)
        df2 = pd.DataFrame(ecr_data)
        # Write each dataframe to a different worksheet.7676
        df1.to_excel(writer, sheet_name='ec2')
        df2.to_excel(writer, sheet_name='ecs')

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()
    except Exception as e:
        exception_handler(e)


def get_ec2_count_account(cloud_list):
    log_frame_debug(logger)
    try:
        ec2_count_account = []
        for accounts in cloud_list:
            account = accounts.get("awsAccountId")
            count = resource_customer_graphql.get_ec2_instances(account, url, auth)
            ec2_count = dict(awsAccountId=accounts.get('awsAccountId'), ec2=count)
            ec2_count_account.append(ec2_count)
        return ec2_count_account
    except Exception as e:
        exception_handler(e)


def adjust_data(vulnerabilities):
    # log_frame_info(logger)
    try:
        foo_items = []
        for item in vulnerabilities.get("items"):
            # To extract out Medium severity findings add "Medium" to the list
            severity_list = ["Critical", "High"]

            # Data from additional source types can be added here by references a different source
            sourceType = "AWS Inspector2"
            if item.get("severity") in severity_list and sourceType in item.get("sources"):
                # Days a vulnerability has remained open
                fr = parse(item.get("firstReported")).date()
                lr = parse(item.get("lastReported")).date()
                delta = lr - fr
                foo_dic = dict(severity=item.get("severity"), days=delta.days)
                foo_items.append(foo_dic)
        vulnerabilities["items"] = foo_items
        vulnerabilities["count"] = len(foo_items)
        if len(foo_items):
            highest = nested_lookup('days', foo_items)
            highest = max(highest)
            vulnerabilities["highest"] = highest
        return vulnerabilities
    except Exception as e:
        exception_handler(e)


def data_processor(data, service):
    log_frame_info(logger)
    try:
        stats = []
        for accounts in data:
            counter = 0
            bucket_lt_30 = []
            bucket_gt_30_lt_60 = []
            bucket_gt_60_lt_90 = []
            bucket_gt_90 = []
            unadjust_counter = 0

            awsAccountId = accounts.get("awsAccountId")
            if accounts.get(service):
                for ec2 in accounts.get(service):
                    ec2["vulnerabilities"] = adjust_data(ec2.get("vulnerabilities"))
                    unadjust_counter = unadjust_counter + 1
                    if ec2.get("vulnerabilities").get("items"):
                        counter = counter + 1
                        bucket_item = ec2.get("vulnerabilities").get("highest")
                        if bucket_item and bucket_item <= 30:
                            bucket_lt_30.append(bucket_item)
                        if bucket_item and bucket_item >= 31 and bucket_item <= 60:
                            bucket_gt_30_lt_60.append(bucket_item)
                        if bucket_item and bucket_item >= 61 and bucket_item <= 90:
                            bucket_gt_60_lt_90.append(bucket_item)
                        if bucket_item and bucket_item >= 91:
                            bucket_gt_90.append(bucket_item)
                inventory = len(accounts.get(service))
                vulnerable = counter

                bucket30 = len(bucket_lt_30)
                bucket30_60 = len(bucket_gt_30_lt_60)
                bucket60_90 = len(bucket_gt_60_lt_90)
                bucket90 = len(bucket_gt_90)
                foo_dic = dict(awsAccountId=awsAccountId, resourceType=service, inventory=inventory,
                               vulnerable=vulnerable, bucket30=bucket30, bucket30_60=bucket30_60,
                               bucket60_90=bucket60_90,
                               bucket90=bucket90)
                stats.append(foo_dic)
            else:
                inventory = 0
                bucket30 = len(bucket_lt_30)
                bucket30_60 = len(bucket_gt_30_lt_60)
                bucket60_90 = len(bucket_gt_60_lt_90)
                bucket90 = len(bucket_gt_90)
                vulnerable = counter
                foo_dic = dict(awsAccountId=awsAccountId, resourceType=service, inventory=inventory,
                               vulnerable=vulnerable, bucket30=bucket30, bucket30_60=bucket30_60,
                               bucket60_90=bucket60_90,
                               bucket90=bucket90)
                stats.append(foo_dic)
        return stats
    except Exception as e:
        exception_handler(e)


def merge_inventory_data(stats, cloud_list):
    try:
        df_resource = pd.DataFrame(stats)
        df_cloud_list = pd.DataFrame(cloud_list)
        cloud_inventory = pd.merge(df_cloud_list, df_resource, on="awsAccountId")
        return cloud_inventory
    except Exception as e:
        print(e)


def data_graber(data, service, cloud_list):
    log_frame_debug(logger)
    try:
        process_data = data_processor(data, service)
        cloud_inventory = merge_inventory_data(process_data, cloud_list)
        return cloud_inventory
    except Exception as e:
        exception_handler(e)


def ecs_data(cloud_list):
    log_frame_debug(logger)
    try:
        service = "ecs"
        data = ecs_count_account(cloud_list)
        resource = data_graber(data, service, cloud_list)
        return resource
    except Exception as e:
        exception_handler(e)


def ec2_data(cloud_list):
    log_frame_debug(logger)
    try:
        service = "ec2"
        data = get_ec2_count_account(cloud_list)
        resource = data_graber(data, service, cloud_list)
        return resource
    except Exception as e:
        exception_handler(e)


def main():
    log_frame_debug(logger)
    global url
    global auth
    try:
        with open('config.yml') as aws_file:
            config = json.load(aws_file)

        url = config.get("url", None)
        auth = str(config.get("auth", None))

        if not auth or not url:
            log_frame_debug(logger, message="Please set URL and Auth token in config.yml")
            sys.exit()

        # Gets information about customer cloud accounts.
        cloud_list = get_cloud_details()
        if not cloud_list:
            log_frame_debug(logger, message="Cloud Accounts not found")
            exit()

        # Gets inventory and vulnerability data for ecs
        ecs = ecs_data(cloud_list)

        # Gets inventory and vulnerability data for ecs

        ec2 = ec2_data(cloud_list)

        # Writes the combined ec2, ecs metrics to an Exel file

        exel_writer(ec2, ecs)

    except Exception as e:
        exception_handler(e)


if __name__ == "__main__":
    main()

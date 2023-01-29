from datetime import datetime
import pandas as pd
import boto3 as aws
import logging
from botocore.exceptions import ClientError
from influxdb import InfluxDBClient
import concurrent.futures


def insert_into_influxdb(patches, instance, influx_client):
    json_body = []
    for patch in patches["Patches"]:
        patch["InstalledTime"] = patch["InstalledTime"].isoformat()
        json_body.append(
            {
                "measurement": "patches",
                "tags": {"instance": instance},
                "time": datetime.now(),
                "fields": patch,
            }
        )
    influx_client.write_points(json_body)


class SSM:
    def __init__(self, ssm_resource):
        self.ssm_resource = ssm_resource

    def get_patch(self, instance):

        try:
            response = self.ssm_resource.describe_instance_patches(
                InstanceId=instance,
                Filters=[
                    {"Key": "State", "Values": ["MISSING", "FAIL"]},
                ],
            )
            logging.info("Got patch result for %s", instance)
            count = len(response["Patches"])

        except ClientError:
            logging.exception("not able to get the patch for %s:", instance)
        else:
            return response


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    df = pd.read_csv("input.csv")
    influx_client = InfluxDBClient("localhost", 8086, "admin", "Password1", "result")
    sdf = df[df["Overall_status"].str.lower() == "success"]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_instance = {}
        for r, rdf in sdf.groupby("region"):
            ssm_client = SSM(aws.client("ssm", r))
            instances = rdf["instance_id"].tolist()
            for instance in instances:
                future = executor.submit(
                    get_patch_and_insert, ssm_client, instance, influx_client
                )
                future_to_instance[future] = instance

        for future in concurrent.futures.as_completed(future_to_instance):
            instance = future_to_instance[future]
            try:
                patches = future.result()
                logging.info(patches)
            except Exception as exc:
                logging.exception(
                    "Error getting patch and inserting for instance %s: %s",
                    instance,
                    exc,
                )


def get_patch_and_insert(ssm_client, instance, influx_client):
    patches = ssm_client.get_patch(instance)
    #insert_into_influxdb(patches, instance, influx_client)
    return patches


if __name__ == "__main__":
    main()

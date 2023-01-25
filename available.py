import json
import boto3 as aws
import logging
from botocore.exceptions import ClientError


class SSM:
    def __init__(self, ssm_resource):
        self.ssm_resource = ssm_resource

    def get_patch(self, instance):

        try:
            response = self.ssm_resource.describe_instance_patches(
                InstanceId=instance,
                Filters=[
                    {
                        'Key': 'State',
                        'Values': [
                            'MISSING', 'FAIL'
                            ]
                    },
                ]
            )
            logging.info("Got patch result for %s", instance)

        except ClientError:
            logging.exception("not able to get the patch for %s:", instance)
        else:
            return response


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ssm_client = SSM(aws.client("ssm", "ap-south-1"))
    patch = ssm_client.get_patch("i-07ce3ecbddb9d08af")
    logging.info(patch)
    with open("output.json", "w") as f:
        json.dump(patch["Patches"], f, indent=4, sort_keys=True, default=str)


if __name__ == "__main__":
    main()

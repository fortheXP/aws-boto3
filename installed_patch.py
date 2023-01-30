import boto3
from datetime import datetime, timedelta, timezone

# create SSM client
client = boto3.client('ssm')

# get current time
now = datetime.now()

# get start time and end time (1 month ago)
current_time = datetime.now(timezone.utc)
start_time = current_time - timedelta(days=30)
end_time = current_time

# describe patches
# instance_id
instance_id='i-0cb8f23b05d1bc28d'

# describe patches
response = client.describe_instance_patches(
    InstanceId=instance_id
)
# filter patches based on installed time
filtered_patches = list(filter(lambda x: start_time <= datetime.strptime(str(x['InstalledTime']), "%Y-%m-%d %H:%M:%S%z") <= end_time, response['Patches']))
# print the filtered patches
print(filtered_patches)


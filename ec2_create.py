import boto3
import jmespath as jp
import time

session = boto3.Session(profile_name='admin')
rs_ec2 = session.resource('ec2')
cl_ec2 = session.client('ec2')

VPC_ID = jp.search('Vpcs[].VpcId',cl_ec2.describe_vpcs())[0]
SUBNET_ID = jp.search('Subnets[?Tags[? Value == `PublicSubnetJenkins`]].SubnetId',cl_ec2.describe_subnets())[0]
SG_ID = jp.search('SecurityGroups[?GroupName == `JenkinsSG`].GroupId',cl_ec2.describe_security_groups())[0]
VOLUME_ID = jp.search('Volumes[?Tags[?Value == `Tools`]].VolumeId',cl_ec2.describe_volumes())[0]
INSTANCE_STATE=""
VOLUME_STATE=""

print("****************** Creating Instance *******************")

rp_ec2 = rs_ec2.create_instances(
    ImageId = "ami-26ebbc5c",
    MinCount = 1,
    MaxCount = 1,
    KeyName = "virginia-key-pair",
    SecurityGroupIds = [SG_ID],
    InstanceType = "t2.micro",
    SubnetId = SUBNET_ID,
)

INSTANCE_ID = rp_ec2[0].id

while INSTANCE_STATE != 'running':
	INSTANCE_STATE=jp.search('Reservations[].Instances[].State[].Name',cl_ec2.describe_instances(InstanceIds=[INSTANCE_ID]))[0]
	time.sleep(5)
	print("Please wait -- " + INSTANCE_ID + " is " + INSTANCE_STATE )

print("EC2 instance with ID - " + INSTANCE_ID + " is " + INSTANCE_STATE + " now.")
print("***************** Attaching Volume *****************")

rp_att_vol = cl_ec2.attach_volume(
    Device='/dev/sdf',
    InstanceId=INSTANCE_ID,
    VolumeId=VOLUME_ID
)

while VOLUME_STATE != 'in-use':
	VOLUME_STATE = jp.search('Volumes[].State',cl_ec2.describe_volumes(VolumeIds=[VOLUME_ID]))[0]
	print("Please wait -- " + VOLUME_ID + " is " + VOLUME_STATE )


print("***************** VPC Details *****************")
print("VPC_ID = "+VPC_ID)
print("SUBNET_ID = "+SUBNET_ID)
print("INSTANCE_ID = "+INSTANCE_ID)
print("SG_ID = "+SG_ID)
print("VOLUME_ID = "+VOLUME_ID)
print("***********************************************")


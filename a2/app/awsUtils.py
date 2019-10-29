import boto3
from app.config import awsConfig

def fetchAllInstances():
    # create connection to ec2
    ec2 = boto3.resource('ec2')
    #    instances = ec2.instances.filter(
    #        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instances = ec2.instances.all()
    
    return instances

def growOneWorker():
    ec2 = boto3.resource('ec2')
    numIns = 0
    instances = ec2.instances.all()
    for instance in instances:
        numIns += 1
    ec2.create_instances(ImageId=awsConfig.imageID, \
        MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName='ece1779')
    newNumIns = 0
    instances = ec2.instances.all()
    for instance in instances:
        newNumIns += 1
    return numIns != newNumIns
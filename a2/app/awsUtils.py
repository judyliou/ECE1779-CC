import boto3
import time

from app.config import awsConfig


class AWSSuite:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')

    """
    retrieve all instances from ec2
    """
    def getAllWorkers(self):
        instances = []
        tagName = str("tag:" + awsConfig.workerTag['key'])
        insFilter = [{
            'Name': tagName,
            'Values': [awsConfig.workerTag['value']]
        }]
        response = self.ec2.describe_instances(Filters=insFilter)
        results = response['Reservations']
        for result in results:
            if len(result['Instances']) > 0:
                if result['Instances'][0]['State']['Name'] != "terminated":
                    instances.append({
                        'Id':
                        result['Instances'][0]['InstanceId'],
                        'State':
                        result['Instances'][0]['State']['Name'],
                        'Port':
                        5000
                    })
        return instances

    """
    fetch one idle target from target group, listen to it's 5000 port
    If no idle, create a new instance from image
    """
    def growOneWorker(self):
        uuInstances = self.getUnusedInstances()
        if not uuInstances:
            instance = self.createOneInstance()
        # use index of id to identify?
        else:
            instance = uuInstances[0]

        # here is the problem: new instance needs some time to run,
        # we need to wait for the start
        # so we give a loop to inquire state of instance until state is running
        stateResponse = self.ec2.describe_instance_status(
            InstanceIds=[instance["Id"]])
        while len(stateResponse['InstanceStatuses']) < 1:
            # jesus this is too much waste
            time.sleep(2)
            stateResponse = self.ec2.describe_instance_status(
                InstanceIds=[instance["Id"]])
        if stateResponse:
            print(stateResponse)
            instance = {
                'Id': stateResponse['InstanceStatuses'][0]['InstanceId'],
            }

        response = self.elb.register_targets(TargetGroupArn=awsConfig.arn,
                                             Targets=[
                                                 {
                                                     'Id': instance['Id'],
                                                     'Port': 5000
                                                 },
                                             ])
        if response and 'ResponseMetadata' in response:
            return True
        # a response verify needed here
        return -1

    """
    retrieve all not working instances in target group
    why there isn't any existing function to retrieve idle workers?
    """
    def getUnusedInstances(self):
        workers = self.getAllWorkers()
        workingWorkers = self.getWorkingInstances()
        uuWorkers = []
        # notice that two list of workers doesn't look the same
        # can't use list minus
        wwIds = []
        for ww in workingWorkers:
            wwIds.append(ww['Id'])
        for worker in workers:
            if worker['Id'] not in wwIds:
                uuWorkers.append(worker)
        return uuWorkers

    """
    retrieve all working instances in target group
    """
    def getWorkingInstances(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=awsConfig.arn, )
        instances = []
        if 'TargetHealthDescriptions' in response:
            for target in response['TargetHealthDescriptions']:
                instances.append({
                    'Id': target['Target']['Id'],
                    'Port': target['Target']['Port'],
                    'State': target['TargetHealth']['State']
                })
        return instances

    """
    create one instance from image
    match image, keypair, *securitygroup, port, *type=worker
    """
    def createOneInstance(self):
        tagName = str("tag:" + awsConfig.workerTag['key'])
        response = self.ec2.run_instances(
            ImageId=awsConfig.imageId,
            KeyName=awsConfig.keypair,
            SecurityGroups=[awsConfig.securityGroup],
            TagSpecifications=[
                {
                    'ResourceType':
                    'instance',
                    'Tags': [
                        {
                            'Key': awsConfig.workerTag['key'],
                            'Value': awsConfig.workerTag['value']
                        },
                    ]
                },
            ],
            MaxCount=1,
            MinCount=1,
            InstanceType='t2.micro')
        instance = None
        if 'Instances' in response and len(response['Instances']) > 0:
            instance = {
                "Id": response['Instances'][0]['InstanceId'],
                'Port': 5000,
                'State': response['Instances'][0]['State']['Name']
            }
        print(instance)
        return instance

    """
    shrink one instance from target group, just remove 1st in list
    if there is none, give user a message
    """
    def shrinkOneWorker(self):
        workingInstances = self.getWorkingInstances()
        if not workingInstances:
            return false
        # use index of id to identify?
        workerToShrink = workingInstances[0]
        response = self.elb.deregister_targets(TargetGroupArn=awsConfig.arn,
                                               Targets=[
                                                   {
                                                       'Id':
                                                       workerToShrink['Id'],
                                                       'Port': 5000,
                                                   },
                                               ])
        # deregister the instance
        if response and 'ResponseMetadata' in response:
            print(response)
        return True

    def stopAllInstances(self):
        return null
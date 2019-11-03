import boto3

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
        insFilter = [{
            'Name': 'tag:type',
            'Values': [awsConfig.workerTag['value']]
        }]
        response = self.ec2.describe_instances(Filters=insFilter)
        # print(response)
        results = response['Reservations']
        for result in results:
            if len(result['Instances']) > 0:
                instances.append({
                    'Id':
                    result['Instances'][0]['InstanceId'],
                    'State':
                    result['Instances'][0]['State']['Name'],
                    #  'Port': 5000
                })
        return instances

    """
    fetch one idle target from target group, listen to it's 5000 port
    If no idle, create a new instance from image
    """
    def growOneWorker(self):
        uuInstances = self.getUnusedInstances()
        numUUIns = len(uuInstances)
        print(numUUIns)
        if numUUIns == 0:
            instance = self.createOneInstance()
        # use index of id to identify?
        instance = uuInstances[0]
        response = self.elb.register_targets(TargetGroupArn=awsConfig.arn,
                                             Targets=[
                                                 {
                                                     'Id': instance['Id'],
                                                     'Port': 5000
                                                 },
                                             ])
        if response and 'ResponseMetadata' in response:
            print(response)
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
        # print(response)
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
        instance = None
        return instance

    """
    shrink one instance from target group, just remove 1st in list
    if there is none, give user a message
    """
    def shrinkOneWorker(self):
        workingInstances = self.getWorkingInstances()
        if not workingInstances:
            return False
        # use index of id to identify?
        workerToShrink = workingInstances[0]
        response = self.elb.deregister_targets(TargetGroupArn=awsConfig.arn,
                                             Targets=[
                                                 {
                                                     'Id': workerToShrink['Id'],
                                                     'Port': 5000,
                                                 },
                                             ])
        # deregister the instance
        if response and 'ResponseMetadata' in response:
            print("response: " + response)
        return True

    def stopAllInstances(self):
        return None
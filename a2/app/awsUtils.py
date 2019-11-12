import boto3
import time
import json
from flask import g
import mysql.connector

from app.config import awsConfig


class AWSSuite:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')
        self.s3 = boto3.client('s3')

    def getWorkersNum(self):
        num = 0
        tagName = str("tag:" + awsConfig.workerTag['key'])
        insFilter = [{
            'Name': tagName,
            'Values': [awsConfig.workerTag['value']]
        }]
        # here we don't want to retrieve other instances than "workers"
        response = self.ec2.describe_instances(Filters=insFilter)
        results = response['Reservations']
        for result in results:
            if len(result['Instances']) > 0:
                # we only need running workers
                if result['Instances'][0]['State']['Name'] != "terminated" and result['Instances'][0]['State']['Name'] != "shutting-down":
                    num += 1
        return num

    """
    retrieve all instances from ec2
    return: list of instances -- workers only
    """
    def getAllWorkers(self):
        instances = []
        tagName = str("tag:" + awsConfig.workerTag['key'])
        insFilter = [{
            'Name': tagName,
            'Values': [awsConfig.workerTag['value']]
        }]
        # here we don't want to retrieve other instances than "workers"
        response = self.ec2.describe_instances(Filters=insFilter)
        results = response['Reservations']
        for result in results:
            if len(result['Instances']) > 0:
                # we only need running workers
                if result['Instances'][0]['State']['Name'] != "terminated" and result['Instances'][0]['State']['Name'] != "shutting-down":
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
    retrieve all instances from ec2
    return: list of instances -- managers only
    """
    def getAllManagers(self):
        instances = []
        tagName = str("tag:" + awsConfig.managerTag['key'])
        insFilter = [{
            'Name': tagName,
            'Values': [awsConfig.managerTag['value']]
        }]
        # here we don't want to retrieve other instances than "workers"
        response = self.ec2.describe_instances(Filters=insFilter)
        results = response['Reservations']
        for result in results:
            if len(result['Instances']) > 0:
                # we only need running workers
                if result['Instances'][0]['State']['Name'] != "terminated" and result['Instances'][0]['State']['Name'] != "shutting-down":
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
    Besides, no more than 10 workers at the same time.
    return: result flag (config in awsConfig)
    """
    def growOneWorker(self):
        # check number of working workers
        workingWorkers = self.getWorkingInstances()
        if len(workingWorkers) >= awsConfig.MAX_INSTANCES:
            return awsConfig.MAX_WORKERS
        uuInstances = self.getUnusedInstances()
        if not uuInstances:
            instance = self.createOneInstance()
        else:
            instance = uuInstances[0]

        if instance is None:
            return awsConfig.CREATE_FAILED
        # guess I need to start the instance whether is running or not
        self.ec2.start_instances(InstanceIds=[instance["Id"]])

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

        # this is even more interesting: you can't register a
        # un-running instance into a target-group, which means you need
        # another loop to wait until it's running
        while stateResponse['InstanceStatuses'][0]['InstanceState'][
                'Name'] != 'running':
            time.sleep(2)
            stateResponse = self.ec2.describe_instance_status(
                InstanceIds=[instance["Id"]])

        if stateResponse:
            instance = {
                'Id': stateResponse['InstanceStatuses'][0]['InstanceId'],
            }

        response = self.elb.register_targets(TargetGroupArn=awsConfig.grougArn,
                                             Targets=[
                                                 {
                                                     'Id': instance['Id'],
                                                     'Port': 5000
                                                 },
                                             ])
        if response and 'ResponseMetadata' in response:
            return awsConfig.REGISTERED
        # a response verify needed here
        return awsConfig.REGISTER_FAILED

    """
    grow workers by number
    return: json object:
            {
                'number': # number of successfully registered,
                'msg': message of response
            }
    """
    def growWorkers(self, num):
        successNum = 0
        for i in range(num):
            res = self.growOneWorker()
            successNum += 1
            if res != awsConfig.REGISTERED:
                return {'number': successNum, 'msg': res}
        return {'number': successNum, 'msg': awsConfig.REGISTERED}

    """
    retrieve all not working instances in target group
    why there isn't any existing function to retrieve idle workers?
    return: a list of unused workers
    """
    def getUnusedInstances(self):
        workers = self.getAllWorkers()
        workingWorkers = self.getWorkingInstances()
        uuWorkers = []
        # notice that two lists of workers don't look the same
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
    return: a list of healthy workers
    """
    def getWorkingInstances(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=awsConfig.grougArn)
        instances = []
        if 'TargetHealthDescriptions' in response:
            for target in response['TargetHealthDescriptions']:
                if target['TargetHealth']['State'] == 'healthy' or target[
                        'TargetHealth']['State'] == 'initial':
                    instances.append({
                        'Id': target['Target']['Id'],
                        'Port': target['Target']['Port'],
                        'State': target['TargetHealth']['State']
                    })
        return instances

    """
    create one instance from image
    match image, keypair, *securitygroup, port, *type=worker
    return: a new instance from image
    """
    def createOneInstance(self):
        tagName = str("tag:" + awsConfig.workerTag['key'])
        response = self.ec2.run_instances(
            ImageId=awsConfig.imageId,
            KeyName=awsConfig.keypair,
            SecurityGroups=[awsConfig.securityGroup],
            Monitoring={'Enabled': True},
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
        return instance

    """
    shrink one instance from target group, just remove 1st in list
    if there is none, give user a message
    if there is no running instances, return a failed
    return: success flag
    """
    def shrinkOneWorker(self):
        workingInstances = self.getWorkingInstances()
        if not workingInstances:
            return awsConfig.NO_WORKER

        # use index of id to identify?
        workerToShrink = workingInstances[0]
        response = self.elb.deregister_targets(
            TargetGroupArn=awsConfig.grougArn,
            Targets=[
                {
                    'Id': workerToShrink['Id'],
                    'Port': 5000,
                },
            ])
        self.ec2.terminate_instances(InstanceIds=[workerToShrink['Id']])
        # deregister the instance
        if response and 'ResponseMetadata' in response:
            return awsConfig.DEREGISTERED
        return awsConfig.DEREGISTER_FAILED

    """
    shrink workers by number
    return: json object
        {
            'number': # instances deregistered,
            'msg': result message
        }
    """
    def shrinkWorkers(self, num):
        successNum = 0
        for i in range(num):
            res = self.shrinkOneWorker()
            successNum += 1
            if res != awsConfig.DEREGISTERED:
                return {'number': successNum, 'msg': res}
        return {'number': successNum, 'msg': awsConfig.DEREGISTERED}

    """
    stop all instances
    """
    def stopManager(self):
        managers = self.getAllManagers()
        managerIds = []
        if not managers:
            return awsConfig.STOP_FAILED
        for manager in managers:
            managerIds.append(manager["Id"])
            print(manager["Id"])
        self.ec2.stop_instances(InstanceIds=managerIds)
        return awsConfig.ALL_STOPED

    """
    """
    def terminateAllWorkers(self):
        instances = self.getAllWorkers()
        instancesIds = []
        if not instances:
            return awsConfig.ALL_STOPED
        for instance in instances:
            instancesIds.append(instance["Id"])   
        response = self.ec2.terminate_instances(InstanceIds=instancesIds)
        if response and 'TerminatingInstances' in response:
            if len(response['TerminatingInstances']) == len(instancesIds):
                return awsConfig.ALL_STOPED
        return awsConfig.STOP_FAILED

    """
    delete all objects in s3 and truncate all tables
    return: message flag
    """
    def deleteAll(self):
        # delete all in s3
        self.deleteAllFromS3()
        # truncate data from rds
        self.truncateAllTables()
        return True

    """
    delete all objects in s3
    """
    def deleteAllFromS3(self):
        objList = self.s3.list_objects(Bucket=awsConfig.s3Bucket)
        if objList and 'Contents' in objList:
            for key in objList['Contents']:
                self.deleteImage(key['Key'])

    """
    delete one file in s3
    """
    def deleteImage(self, key):
        self.s3.delete_object(
            Bucket=awsConfig.s3Bucket,
            Key=key,
        )

    """
    truncate two tables in database: users and photos
    """
    def truncateAllTables(self):
        cnx = self.get_db()
        cursor = cnx.cursor()
        truncateUsers = '''truncate table users'''
        truncatePhotos = '''truncate table photos'''
        cursor.execute(truncateUsers, )
        cursor.execute(truncatePhotos, )
        cnx.commit()

    def connect_to_database(self):
        return mysql.connector.connect(user=awsConfig.dbConfig['user'],
                                       password=awsConfig.dbConfig['password'],
                                       host=awsConfig.dbConfig['host'],
                                       database=awsConfig.dbConfig['database'])

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = self.connect_to_database()
        return db

    def fetchConfig(self):
        cnx = self.get_db()
        cursor = cnx.cursor()
        sQuery = "select * from a2.auto_config"
        cursor.execute(sQuery)
        config = cursor.fetchone()
        if config is not None:
            ratio = config[0]
            thresholdHigh = config[1]
            thresholdLow = config[2]
        return ratio, thresholdHigh, thresholdLow

    def changeConfig(self, ratioHigh, rationLow, thresholdHigh, thresholdLow):
        cnx = self.get_db()
        cursor = cnx.cursor()
        tQuery = "truncate table a2.auto_config"
        iQuery = "insert into a2.auto_config values (%s, %s, %s, %s) "
        cursor.execute(tQuery)
        cnx.commit()
        cursor.execute(iQuery, (ratioHigh, rationLow, thresholdHigh, thresholdLow, ))
        cnx.commit()
        
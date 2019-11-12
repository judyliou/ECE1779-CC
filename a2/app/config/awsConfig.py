"""
    please copy your config info here and comment
    others' info. Don't delete other's info here.
    Thanks.
"""

####### some consts
# grow workers
MAX_WORKERS = 10000
REGISTERED = 10001
REGISTER_FAILED = 10002
# create instance
CREATE_FAILED = 10003
# shrink workers
NO_WORKER = 10004
DEREGISTERED = 10005
DEREGISTER_FAILED = 10006
# stop
ALL_STOPED = 10007
STOP_FAILED = 10008

MAX_INSTANCES = 10

####### Junbang's config #######
imageId = "ami-027dc50ffd664187b"
grougArn = "arn:aws:elasticloadbalancing:us-east-1:735141600372:targetgroup/a1group/bb2f4c7ebd44cf9b"
workerTag = {"key": "type", "value": "worker"}
managerTag = {"key": "type", "value": "manager"}
keypair = "ece1779_a1"
securityGroup = "launch-wizard-3"
s3Bucket = "ece1779testbucket"
dbConfig = {'user': 'admin',
             'password': 'ece1779pass',
             'host': 'db1779.c3pmiawhpay4.us-east-1.rds.amazonaws.com',
             'database': 'a1'}

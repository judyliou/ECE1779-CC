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

MAX_INSTANCES = 4

####### Junbang's config #######
imageId = "ami-00faef86802f615d4"
grougArn = "arn:aws:elasticloadbalancing:us-east-1:350581778973:targetgroup/imageGroup/05ccba24a0a8b376"
workerTag = {"key": "type", "value": "worker"}
keypair = "ece1779"
securityGroup = "launch-wizard-1"
s3Bucket = "ece1779-junbang-a1"
dbConfig = {'user': 'admin',
             'password': 'ece1779pass',
             'host': 'a1-db.cou8dzlst8q4.us-east-1.rds.amazonaws.com',
             'database': 'a1'}

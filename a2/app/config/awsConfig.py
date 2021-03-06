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

# ####### Junbang's config #######
# imageId = "ami-0504cab097c420742"
# grougArn = "arn:aws:elasticloadbalancing:us-east-1:350581778973:targetgroup/imageGroup/05ccba24a0a8b376"
# workerTag = {"key": "type", "value": "worker"}
# keypair = "ece1779"
# securityGroup = "launch-wizard-1"

####### You-Syuan's config #######
imageId = "ami-0504cab097c420742"
grougArn = "arn:aws:elasticloadbalancing:us-east-1:735141600372:targetgroup/a1group/bb2f4c7ebd44cf9b"
workerTag = {"key": "type", "value": "worker"}
keypair = "ece1779_a1"
securityGroup = "launch-wizard-3"
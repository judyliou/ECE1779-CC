import boto3
from datetime import datetime, timedelta
from app.utils import *
from app import awsUtils


# connect to DB and access the auto-scaling configure
cnx = get_db()
cursor = cnx.cursor()
query = '''SELECT * FROM auto_config LIMIT 1''' 
cursor.execute(query)
config = cursor.fetchone()

ratio, threshold = config[0], config[1] * 0.8
flag = 0

# connect to CloudWatch
client = boto3.client('cloudwatch')
cpu = client.get_metric_statistics( 
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*2),
        EndTime = datetime.utcnow(),
        MetricName = 'CPUUtilization',
        Namespace = 'AWS/EC2',
        Statistics = ['Average']
    )
cpu_record = []
for point in cpu['Datapoints']:
    cpu_record.append(point['Average'])


# Alter worker pool
awsSuite = awsUtils.AWSSuite()

if sum(cpu_record)/len(cpu_record) > threshold:
    awsSuite.growWorker(ratio)
    flag = 1
    # when to set flag back to 0????
elif sum(cpu_record)/len(cpu_record) > threshold:
    awsSuite.shrinkWorker(ratio)
    flag = 1

import boto3
from datetime import datetime, timedelta
import threading

from app.utils import *
from app import awsUtils
from app.config import awsConfig

awsSuite = awsUtils.AWSSuite()
cloudwatch = boto3.client('cloudwatch')


def fetch_policy():
    # connect to DB and access the auto-scaling configure
    cnx = connect_to_database()
    cursor = cnx.cursor()
    query = '''SELECT * FROM auto_config LIMIT 1''' 
    cursor.execute(query)
    config = cursor.fetchone()

    ratio_high, ratio_low, threshold_high, threshold_low = config[0], config[1], config[2] * 0.9, config[3] * 1.1
    return ratio_high, ratio_low, threshold_high, threshold_low

def check_status(flag):
    ratio_high, ratio_low, threshold_high, threshold_low = fetch_policy()

    # get CPU data
    cpu = cloudwatch.get_metric_statistics( 
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*2),
        EndTime = datetime.utcnow(),
        MetricName = 'CPUUtilization',
        Namespace = 'AWS/EC2',
        Statistics = ['Average'],
        Dimensions= [{'Name': 'ImageId', 'Value': awsConfig.imageId}]
    )
    cpu_record = []
    print('cpu data point:', len(cpu['Datapoints']))
    for point in cpu['Datapoints']:
        cpu_record.append(point['Average'])
    if len(cpu_record) == 0:
        avg_CPU = 0
    else:
        avg_CPU = sum(cpu_record)/len(cpu_record)
    print(avg_CPU)

    # check wether over the threshold
    if flag == 0:
        num_workers = awsSuite.getWorkersNum()
        if avg_CPU >= threshold_high:
<<<<<<< HEAD
            num_new_workers = num_workers * (ratio - 1)
=======
            num_new_workers = num_workers * (ratio_high - 1)
>>>>>>> e0599df3975ed1c1dd5bb2b3fc1f495c2e0c6c3b
            print('over threshold, add ', num_new_workers, " workers")
            awsSuite.growWorkers(num_new_workers)
            flag = 1
        elif avg_CPU <= threshold_low:
<<<<<<< HEAD
            num_new_workers = int((num_workers / ratio) * (ratio - 1))
=======
            num_new_workers = int((num_workers / ratio_low) * (ratio_low - 1))
>>>>>>> e0599df3975ed1c1dd5bb2b3fc1f495c2e0c6c3b
            print('under threshold, shut ', num_new_workers, " workers")
            awsSuite.shrinkWorkers(num_new_workers)
            flag = 1
    else:  # still creating/deleting instances
        if avg_CPU < threshold_high and avg_CPU > threshold_low:
            print('set flag back to 0')
            flag = 0

    # Set a timer for checking every two minutes
    timer = threading.Timer(20, check_status, [flag])
    timer.start()    

if __name__ == "__main__":
    flag = 0
    check_status(flag)
from flask import render_template, url_for, request, redirect
from app import webapp
import boto3
from datetime import datetime, timedelta
from operator import itemgetter
import time




@webapp.route("/workers", methods=['GET'])
# Display list of all workers
def workerList():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    return render_template("workerList.html", title='Workers', instances=instances)


@webapp.route("/viewWorker/<id>", methods=['GET'])
# Display details (CPU utilization and HTTP requests received) of a certain worker
def viewWorker(id):
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(id)
    client = boto3.client('cloudwatch', region_name='us-east-1')

    # CPU utilization
    cpu = client.get_metric_statistics( 
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*30),
        EndTime = datetime.utcnow(),
        MetricName = 'CPUUtilization',
        Namespace = 'AWS/EC2',
        Statistics = ['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []
    for point in cpu['Datapoints']:
        # hour = point['Timestamp'].hour
        # minute = point['Timestamp'].minute
        # time = hour + minute/60
        time = point['Timestamp'].timestamp( )*1000
        cpu_stats.append([time, point['Average']])
    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    # HTTP request
    http_in = client.get_metric_statistics(
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*30),
        EndTime = datetime.utcnow(),
        MetricName = 'HTTPRequest',
        Namespace = 'Custom',
        Statistics = ['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
   
    http_stats = []
    for point in http_in['Datapoints']:
        # hour = point['Timestamp'].hour
        # minute = point['Timestamp'].minute
        # time = hour + minute/60
        time = point['Timestamp'].timestamp( )*1000
        http_stats.append([time, point['Sum']])
    http_stats = sorted(http_stats, key=itemgetter(0))
    # print('cpu:', cpu_stats)
    # print('http:', http_stats)
    return render_template("workerInfo.html", 
                            worker=id,   
                            instance=instance,
                            cpu_stats=cpu_stats,
                            http_stats=http_stats)



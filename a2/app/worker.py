from flask import render_template, url_for, request, redirect
from app import webapp
import boto3
from datetime import datetime, timedelta
from operator import itemgetter

@webapp.route("/workers", method=['GET'])
# Display list of all workers
def workerList():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    return render_template("workerList.html", title='Workers', instances=instances)


@webapp.route("/viewWorker/<id>", methods=['GET'])
# Display details (CPU utilization and HTTP requests received) of a certain worker
def viewWorker(id):
    ec2 = boto3.resource('ec2')
    instance = ec2.instnace(id)
    client = boto3.client('cloudwatch')

    # CPU utilization
    cpu = client.get_metric_statistics( 
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*30),
        EndTime = datetime.utcnow(),
        MetricName = 'CPUUtilization',
        NameSpace = 'AWS/EC2',
        Statistics = ['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []
    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append(time, point['Sum'])
    cpu_stats = sorted(cpu_stats, key=itemgetter(0))


    # HTTP request
    HTTP_in = client.get_metric_statistics(
        Period=60,
        StartTime = datetime.utcnow() - timedelta(seconds=60*30),
        EndTime = datetime.utcnow(),
        MetricName = 'HTTPRequest',
        NameSpace = 'MyNameSpace',
        Statistics = ['SampleCount'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
   
    HTTP_stats = []
    for point in HTTP_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        HTTP_stats.append([time, point['SampleCount']])
    HTTP_stats = sorted(HTTP_stats, key=itemgetter(0))

    return render_template("workerInfo.html", 
                            worker=id,   
                            instance=instance,
                            cpu_stats=cpu_stats,
                            HTTP_stats=HTTP_stats)

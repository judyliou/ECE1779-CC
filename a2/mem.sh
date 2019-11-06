#!/bin/bash
HTTP_REQ=$(netstat -a | grep ESTABLISHED | grep -c :5000)
EC2_INSTANCE_ID=$(ec2metadata --instance-id)

aws cloudwatch put-metric-data --metric-name HTTPRequest --dimensions InstanceId=$EC2_INSTANCE_ID --namespace "Custom" --value $HTTP_REQ

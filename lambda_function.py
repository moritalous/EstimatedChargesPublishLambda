import boto3
import json
import os
import datetime

def get_metric_from_cloudwatch():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    
    client = boto3.client('cloudwatch', region_name='us-east-1')
    
    response = client.get_metric_statistics(
        Namespace = 'AWS/Billing',
        MetricName = 'EstimatedCharges',
        Dimensions = [{
                'Name': 'Currency',
                'Value': 'USD'
            },],
        StartTime = yesterday,
        EndTime = today,
        Period = 86400,
        Statistics = ['Sum'],
        )
    
    print('Cloudwatch get_metric_statistics result:')
    print(response)
    
    return response

def notify_by_sns(EstimatedCharges):
    client = boto3.client('sns')
    
    timestamp = EstimatedCharges['Datapoints'][0]['Timestamp']
    sum = EstimatedCharges['Datapoints'][0]['Sum']
    
    topic_arn = os.environ.get('TOPIC_ARN', '')
    if topic_arn == '':
        return
    
    message = f'timestamp : {timestamp}, EstimatedCharges : ${sum}'
    
    response = client.publish(
        TopicArn = topic_arn,
        Message = message
        )
    
    print('SNS publish result:')
    print(response)

def lambda_handler(event, context):
    metric = get_metric_from_cloudwatch()
    
    notify_by_sns(metric)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

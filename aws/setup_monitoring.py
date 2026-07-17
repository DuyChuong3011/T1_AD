import boto3

REGION = 'ap-southeast-1'
ACCOUNT_ID = '036071344072'
ENDPOINT_NAME = 'scada-fault-predictor-v1'

cw = boto3.client('cloudwatch', region_name=REGION)
sns_client = boto3.client('sns', region_name=REGION)

def create_sns_topic(email):
    topic = sns_client.create_topic(Name='scada-fault-alerts')
    topic_arn = topic['TopicArn']
    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )
    print(f"SNS Topic ARN: {topic_arn}")
    print(f"Kiểm tra email {email} và bấm Confirm!")
    return topic_arn

def create_endpoint_error_alarm(topic_arn):
    cw.put_metric_alarm(
        AlarmName='SCADA-Endpoint-Errors',
        MetricName='ModelError',
        Namespace='AWS/SageMaker',
        Statistic='Sum',
        Period=300,
        EvaluationPeriods=1,
        Threshold=5,
        ComparisonOperator='GreaterThanThreshold',
        Dimensions=[{
            'Name': 'EndpointName',
            'Value': ENDPOINT_NAME
        }],
        AlarmActions=[topic_arn]
    )
    print("Alarm: Endpoint Errors created")

def create_latency_alarm(topic_arn):
    cw.put_metric_alarm(
        AlarmName='SCADA-High-Latency',
        MetricName='ModelLatency',
        Namespace='AWS/SageMaker',
        Statistic='Average',
        Period=300,
        EvaluationPeriods=1,
        Threshold=2000,
        ComparisonOperator='GreaterThanThreshold',
        Dimensions=[{
            'Name': 'EndpointName',
            'Value': ENDPOINT_NAME
        }],
        AlarmActions=[topic_arn]
    )
    print("Alarm: High Latency created")

if __name__ == '__main__':
    EMAIL = 'trannhunhathoangaws1@gmail.com'  # Đổi thành email nhóm
    topic_arn = create_sns_topic(EMAIL)
    create_endpoint_error_alarm(topic_arn)
    create_latency_alarm(topic_arn)
    print("Setup monitoring xong!")
    print(f"Điền SNS_TOPIC_ARN này vào handler.py:")
    print(f"SNS_TOPIC_ARN = 'arn:aws:sns:{REGION}:{ACCOUNT_ID}:scada-fault-alerts'")
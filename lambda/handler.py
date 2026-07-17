import json
import boto3

runtime = boto3.client('sagemaker-runtime',
                        region_name='ap-southeast-1')
sns = boto3.client('sns',
                    region_name='ap-southeast-1')

# Đúng tên cột diff của dataset SCADA
DIFF_COLS = [
    'LV ActivePower (kW)_diff_1',
    'Wind Speed (m/s)_diff_1',
    'Theoretical_Power_Curve (KWh)_diff_1'
]
ENDPOINT_NAME = 'scada-fault-predictor-v1'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-southeast-1:036071344072:scada-fault-alerts'
THRESHOLD = 0.3


def parse_input(event):
    if isinstance(event.get('body'), str):
        body = json.loads(event['body'])
    elif isinstance(event.get('body'), dict):
        body = event['body']
    else:
        body = event
    sensors = body['sensors']
    timestamp = body.get('timestamp', 'N/A')
    return sensors, timestamp


def build_payload(sensors):
    header = ','.join(DIFF_COLS)
    values = ','.join([str(sensors.get(col, 0)) for col in DIFF_COLS])
    return header + '\n' + values


def call_endpoint(payload):
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='text/csv',
        Body=payload
    )
    result = response['Body'].read().decode().strip()
    prob = float(result)
    return prob


def determine_severity(prob):
    if prob > 0.9:
        return 'CRITICAL'
    elif prob > 0.75:
        return 'HIGH'
    elif prob > 0.5:
        return 'MEDIUM'
    else:
        return 'LOW'


def send_alert(prob, severity, timestamp):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f'SCADA Alert: {severity}',
        Message=f"""
Phát hiện nguy cơ sự cố!
Thời gian:  {timestamp}
Xác suất:   {prob:.2%}
Mức độ:     {severity}
        """
    )


def lambda_handler(event, context):
    try:
        sensors, timestamp = parse_input(event)
        payload = build_payload(sensors)
        fault_prob = call_endpoint(payload)
        severity = determine_severity(fault_prob)

        if fault_prob > THRESHOLD:
            send_alert(fault_prob, severity, timestamp)

        result = {
            'fault_probability': round(fault_prob, 4),
            'alert': fault_prob > THRESHOLD,
            'severity': severity,
            'timestamp': timestamp
        }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


if __name__ == '__main__':
    test_event = {
        'body': json.dumps({
            'sensors': {
                'Accelerometer1RMS_diff': 0.1,
                'Accelerometer2RMS_diff': 0.05,
                'Current_diff': 0.3,
                'Pressure_diff': 0.2,
                'Temperature_diff': 1.5,
                'Thermocouple_diff': 1.2,
                'Voltage_diff': 0.0,
                'Volume Flow RateRMS_diff': -0.1
            },
            'timestamp': '2026-07-14T10:00:00'
        })
    }
    sensors, timestamp = parse_input(test_event)
    payload = build_payload(sensors)
    print(f"Parse OK: {timestamp}")
    print(f"Payload:\n{payload}")
    print("Handler test xong!")
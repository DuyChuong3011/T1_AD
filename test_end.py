import boto3

sm = boto3.client('sagemaker', region_name='ap-southeast-1')

steps = sm.list_pipeline_execution_steps(
    PipelineExecutionArn='arn:aws:sagemaker:ap-southeast-1:036071344072:pipeline/scada-ml-pipeline/execution/3ki797wcxt09'
)

for step in steps['PipelineExecutionSteps']:
    print(f"Step: {step['StepName']}")
    print(f"Status: {step['StepStatus']}")
    if 'FailureReason' in step:
        print(f"Loi: {step['FailureReason']}")
    print()
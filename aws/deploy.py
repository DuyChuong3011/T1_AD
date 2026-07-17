import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel

ROLE = 'arn:aws:iam::036071344072:role/SageMakerExecutionRole-MLOps'
REGION = 'ap-southeast-1'
ENDPOINT_NAME = 'scada-fault-predictor-v1'

# Cập nhật sau khi B train xong và gửi path mới
MODEL_ARTIFACT = 's3://sagemaker-ap-southeast-1-036071344072/scada-gmm-2026-07-15-09-07-03-370/output/model.tar.gz'  # B điền vào đây sau khi train xong


def deploy_model():
    session = sagemaker.Session()
    model = SKLearnModel(
        model_data=MODEL_ARTIFACT,
        role=ROLE,
        entry_point='src/train.py',
        framework_version='1.2-1',
        sagemaker_session=session
    )
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type='ml.t2.medium',
        endpoint_name=ENDPOINT_NAME
    )
    print(f"Endpoint deployed: {ENDPOINT_NAME}")
    return predictor


def delete_endpoint():
    sm = boto3.client('sagemaker', region_name=REGION)
    sm.delete_endpoint(EndpointName=ENDPOINT_NAME)
    print(f"Endpoint deleted: {ENDPOINT_NAME}")


def delete_endpoint_config():
    sm = boto3.client('sagemaker', region_name=REGION)
    sm.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
    print(f"EndpointConfig deleted: {ENDPOINT_NAME}")


if __name__ == '__main__':
    deploy_model()
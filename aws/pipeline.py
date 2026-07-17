import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.conditions import ConditionGreaterThan
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.functions import JsonGet

ROLE = 'arn:aws:iam::036071344072:role/SageMakerExecutionRole-MLOps'
BUCKET = 'scada-fault-prediction'
REGION = 'ap-southeast-1'


def build_pipeline():
    session = sagemaker.Session()

    # ── Bước 1: Processing ──
    processor = SKLearnProcessor(
        framework_version='1.2-1',
        role=ROLE,
        instance_type='ml.m5.large',
        instance_count=1,
        sagemaker_session=session
    )

    step_process = ProcessingStep(
        name='ScadaProcessing',
        processor=processor,
        code='src/feature_engineering.py',
        inputs=[
            ProcessingInput(
                source=f's3://{BUCKET}/raw/',
                destination='/opt/ml/processing/input'
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name='features',
                source='/opt/ml/processing/output',
                destination=f's3://{BUCKET}/features/'
            )
        ]
    )

    # ── Bước 2: Training ──
    estimator = SKLearn(
        entry_point='src/train.py',
        framework_version='1.2-1',
        role=ROLE,
        instance_type='ml.m5.large',
        instance_count=1,
        hyperparameters={'n_components': 5},
        sagemaker_session=session
    )

    step_train = TrainingStep(
        name='ScadaTraining',
        estimator=estimator,
        inputs={
            'train': sagemaker.inputs.TrainingInput(
                s3_data=f's3://{BUCKET}/features/',
                content_type='text/csv'
            )
        }
    )

    # ── Bước 3: Evaluate ──
    eval_processor = SKLearnProcessor(
        framework_version='1.2-1',
        role=ROLE,
        instance_type='ml.m5.large',
        instance_count=1,
        sagemaker_session=session
    )

    evaluation_report = PropertyFile(
        name='EvaluationReport',
        output_name='evaluation',
        path='evaluation.json'
    )

    step_evaluate = ProcessingStep(
        name='ScadaEvaluate',
        processor=eval_processor,
        code='src/evaluate.py',
        inputs=[
            ProcessingInput(
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                destination='/opt/ml/processing/model'
            ),
            ProcessingInput(
                source=f's3://{BUCKET}/features/',
                destination='/opt/ml/processing/test'
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name='evaluation',
                source='/opt/ml/processing/evaluation',
                destination=f's3://{BUCKET}/evaluation/'
            )
        ],
        job_arguments=[
            '--model-dir', '/opt/ml/processing/model',
            '--test', '/opt/ml/processing/test',
            '--output-dir', '/opt/ml/processing/evaluation'
        ],
        property_files=[evaluation_report]
    )

    # ── Bước 4: Condition ──
    condition = ConditionGreaterThan(
        left=JsonGet(
            step_name=step_evaluate.name,
            property_file=evaluation_report,
            json_path='metrics.auc.value'
        ),
        right=0.7
    )

    # ── Bước 5: Register ──
    step_register = RegisterModel(
        name='ScadaRegister',
        estimator=estimator,
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        content_types=['text/csv'],
        response_types=['text/csv'],
        inference_instances=['ml.t2.medium'],
        transform_instances=['ml.m5.large'],
        model_package_group_name='scada-fault-models',
        approval_status='Approved'
    )

    step_condition = ConditionStep(
        name='CheckModelQuality',
        conditions=[condition],
        if_steps=[step_register],
        else_steps=[]
    )

    # ── Ghép pipeline ──
    pipeline = Pipeline(
        name='scada-ml-pipeline',
        steps=[
            step_process,
            step_train,
            step_evaluate,
            step_condition
        ],
        sagemaker_session=session
    )

    return pipeline


def run_pipeline():
    pipeline = build_pipeline()
    pipeline.upsert(role_arn=ROLE)
    execution = pipeline.start()
    print(f"Pipeline started: {execution.arn}")
    print("Vào Console → SageMaker → Pipelines để xem tiến trình")


if __name__ == '__main__':
    run_pipeline()
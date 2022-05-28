#-*- encoding:utf-8 -*-
import uuid
from logging import getLogger, StreamHandler, DEBUG
import os
# Third Party
import boto3


# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

# EMR
emr_serverless = boto3.client('emr-serverless')

def start_job_run():
    client_token = str(uuid.uuid4())
    EMR_APPLICATION_ID = os.environ["EMR_APPLICATION_ID"]
    EMR_EXECUTION_ROLE_ARN = os.environ["EMR_EXECUTION_ROLE_ARN"]
    EMR_S3_BUCKET = os.environ["EMR_S3_BUCKET"]

    emr_serverless.start_job_run(
        applicationId=EMR_APPLICATION_ID,
        clientToken=client_token,
        executionRoleArn=EMR_EXECUTION_ROLE_ARN,
        jobDriver={
            'sparkSubmit': {
                'entryPoint': f"s3://{EMR_S3_BUCKET}/EMR/scripts/main.py",
                'sparkSubmitParameters': " ".join([
                    f"--conf {key}={value}" for key, value in {
                        # https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/using-python-libraries.html
                        "spark.archives": f"s3://{EMR_S3_BUCKET}/EMR/scripts/pyspark_venv.tar.gz#environment",
                        "spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON": "./environment/bin/python",
                        "spark.emr-serverless.driverEnv.PYSPARK_PYTHON": "./environment/bin/python",
                        "spark.emr-serverless.executorEnv.PYSPARK_PYTHON": "./environment/bin/python"
                    }.items()
                ])
            },
        },
        configurationOverrides={
            'monitoringConfiguration': {
                's3MonitoringConfiguration': {
                    'logUri': f"s3://{EMR_S3_BUCKET}/EMR/logs",
                },
            }
        },
        executionTimeoutMinutes=5,
        name='job'
    )

def lambda_handler(_, __):
    start_job_run()

if __name__ == "__main__":
    lambda_handler({},{})

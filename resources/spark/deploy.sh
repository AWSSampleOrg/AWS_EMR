#!/usr/bin/env bash

set -euo pipefail

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

STACK_NAME="EMR-Docker-Spark"
profile="default"
AWS_REGION=$(aws configure get region --profile ${profile})
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile ${profile})

S3_BUCKET="your-bucket-name"

aws cloudformation deploy \
    --template-file template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        EmrLogUri=s3://${S3_BUCKET}/EMR/logs \
        EcrImage=pyspark \
        EcrImageTag=latest \
   --capabilities CAPABILITY_NAMED_IAM

#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

EMR_LOG_BUCKET="your-bucket-name"
STACK_NAME="EMR-Docker-Serverless-Spark"

aws cloudformation deploy \
    --template-file template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        EmrLogBucket=${EMR_LOG_BUCKET} \
    --capabilities CAPABILITY_NAMED_IAM

#!/usr/bin/env bash

set -euo pipefail

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

profile="default"
AWS_REGION=$(aws configure get region --profile ${profile})
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile ${profile})
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
EC2_KEY_PAIR=""
SUBNET_ID=""

# create cluster
sed -e "s/%ECR_REPOSITORY%/${ECR_REPOSITORY}/g" \
    -e "s/%YARN_CONTAINER_RUNTIME_DOCKER_IMAGE%/${ECR_REPOSITORY}\/pyspark:latest/g" \
    base-emr-configuration.json > emr-configuration.json

aws emr create-cluster \
    --name 'EMR 6.6.0 with Docker' \
    --release-label emr-6.6.0 \
    --applications Name=Livy Name=Spark \
    --ec2-attributes "KeyName=${EC2_KEY_PAIR},SubnetId=${SUBNET_ID}" \
    --instance-type m1.small \
    --instance-count 3 \
    --use-default-roles \
    --configurations file://./emr-configuration.json 2> failure.txt

# success
echo -e "\033[34m${STACK_NAME} has successfully deployed!!\033[0m"

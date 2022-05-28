#!/usr/bin/env bash

set -euo pipefail

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

profile="default"
AWS_REGION=$(aws configure get region --profile ${profile})
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile ${profile})
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_IMAGE="pyspark"


# build
. ${SOURCE_DIR}/build.sh

# login
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR}

# push
image_tag="latest"

docker image tag pyspark:latest ${ECR_REPOSITORY}/${ECR_IMAGE}:${image_tag}
docker image push ${ECR_REPOSITORY}/${ECR_IMAGE}:${image_tag}

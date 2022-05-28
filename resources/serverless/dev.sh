#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

export $(cat ${SOURCE_DIR}/.env | grep -v ^\#)

python ${SOURCE_DIR}/src/spark_submit.py

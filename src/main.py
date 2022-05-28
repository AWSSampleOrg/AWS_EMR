#-*- encoding:utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
from pyspark.sql import SparkSession
import boto3
import sys
import socket

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

def main():
    logger.debug("Hello World")
    logger.debug(sys.version_info)
    logger.debug(__file__)
    logger.debug(socket.gethostname())
    SparkSession.builder.appName("app").enableHiveSupport().getOrCreate()
    boto3.client("s3")

if __name__ == "__main__":
    main()

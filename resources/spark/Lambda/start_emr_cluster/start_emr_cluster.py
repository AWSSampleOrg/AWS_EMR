#-*- encoding:utf-8 -*-
import json
from logging import getLogger, StreamHandler, DEBUG
import os,os.path
import boto3

#logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

#EMR
emr = boto3.client("emr")


def is_emr_cluster_exists():
    cluster_name = os.environ["EMR_NAME"]
    return any([
        cluster["Name"] == cluster_name
        for cluster in emr.list_clusters(
            ClusterStates = [
                "STARTING",
                "BOOTSTRAPPING",
                "RUNNING",
                "WAITING"
            ]
    	)["Clusters"]
    ])

def get_configurations():
    ECR_REGISTRY = os.environ["ECR_REGISTRY"]
    YARN_CONTAINER_RUNTIME_DOCKER_IMAGE = os.environ["YARN_CONTAINER_RUNTIME_DOCKER_IMAGE"]
    return [
        {
            "Classification": "container-executor",
            "Properties": {},
            "Configurations": [
            {
                "Classification": "docker",
                "Properties": {
                "docker.privileged-containers.registries": f"local,centos,{ECR_REGISTRY}",
                "docker.trusted.registries": f"local,centos,{ECR_REGISTRY}"
                }
            }
            ]
        },
        {
            "Classification": "livy-conf",
            "Properties": {
            "livy.spark.master": "yarn",
            "livy.spark.deploy-mode": "cluster",
            "livy.server.session.timeout": "16h"
            }
        },
        {
            "Classification": "hive-site",
            "Properties": { "hive.execution.mode": "container" }
        },
        {
            "Classification": "spark-defaults",
            "Properties": {
            "spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE": "docker",
            "spark.yarn.am.waitTime": "300s",
            "spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE": "docker",
            "spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG": "hdfs:///user/hadoop/config.json",
            "spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE": YARN_CONTAINER_RUNTIME_DOCKER_IMAGE,
            "spark.executor.instances": "2",
            "spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG": "hdfs:///user/hadoop/config.json",
            "spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE": YARN_CONTAINER_RUNTIME_DOCKER_IMAGE
            }
        }
    ]

def start_emr_cluster():
    response = emr.run_job_flow(
        Applications=[
            {"Name": "Livy"},
            {"Name": "Spark"}
        ],
        AutoScalingRole = os.environ["EMR_AUTOSCALING_DEFAULT_ROLE"],
        Configurations = get_configurations(),
        Instances={
            "Ec2KeyName": "string",
            "EmrManagedMasterSecurityGroup" : os.environ["EMR_MANAGED_MASTER_SECURITYGROUP"],
            "EmrManagedSlaveSecurityGroup" : os.environ["EMR_MANAGED_SLAVE_SECURITYGROUP"],
            # Launch Type of EMR ClusterType should be true, Step action type should be false
            "KeepJobFlowAliveWhenNoSteps" : True,
            # https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-sg-specify.html
            # "ServiceAccessSecurityGroup" : os.environ["EMR_SERVICE_ACCESS_SECURITYGROUP"],
            "TerminationProtected": False,
            # "MasterInstanceType": "string",
            # "SlaveInstanceType": "string",
            # "InstanceCount": 123,
            ##################################################
            # the instance fleet configuration
            ##################################################
            # "InstanceFleets": [
            #     {
            #         "Name": "string",
            #         "InstanceFleetType": "MASTER"|"CORE"|"TASK",
            #         "TargetOnDemandCapacity": 123,
            #         "TargetSpotCapacity": 123,
            #         "InstanceTypeConfigs": [
            #             {
            #                 "InstanceType": "string",
            #                 "WeightedCapacity": 123,
            #                 # The core instance fleet uses a maximum Spot price (BidPrice) as a percentage of On-Demand,
            #                 # while the task and master instance fleets use a maximum Spot price (BidPriceAsPercentageofOnDemandPrice) as a string in USD.
            #                 "BidPrice": "string",
            #                 "BidPriceAsPercentageOfOnDemandPrice": 123.0,
            #                 "EbsConfiguration": {
            #                     "EbsBlockDeviceConfigs": [
            #                         {
            #                             "VolumeSpecification": {
            #                                 "VolumeType": "string",
            #                                 "Iops": 123,
            #                                 "SizeInGB": 123
            #                             },
            #                             "VolumesPerInstance": 123
            #                         },
            #                     ],
            #                     "EbsOptimized": True|False
            #                 },
            #                 "Configurations": [
            #                     {
            #                         "Classification": "string",
            #                         "Configurations": {"... recursive ..."},
            #                         "Properties": {
            #                             "string": "string"
            #                         }
            #                     },
            #                 ],
            #                 "CustomAmiId": "string"
            #             },
            #         ],
            #         "LaunchSpecifications": {
            #             "SpotSpecification": {
            #                 "TimeoutDurationMinutes": 123,
            #                 "TimeoutAction": "SWITCH_TO_ON_DEMAND"|"TERMINATE_CLUSTER",
            #                 "BlockDurationMinutes": 123,
            #                 "AllocationStrategy": "capacity-optimized"
            #             },
            #             "OnDemandSpecification": {
            #                 "AllocationStrategy": "lowest-price",
            #                 "CapacityReservationOptions": {
            #                     "UsageStrategy": "use-capacity-reservations-first",
            #                     "CapacityReservationPreference": "open"|"none",
            #                     "CapacityReservationResourceGroupArn": "string"
            #                 }
            #             }
            #         }
            #     },
            # ],
            # "Ec2SubnetIds": [
            #     "string",
            # ],
            ##################################################
            # the uniform instance group configuration
            ##################################################
            "InstanceGroups": [
                {
                    "Market": "ON_DEMAND",
                    "InstanceRole": "MASTER",
                    "InstanceType": "m1.small",
                    "InstanceCount": 1
                },
                {
                    "Market": "ON_DEMAND",
                    "InstanceRole": "CORE",
                    # https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-supported-instance-types.html
                    "InstanceType": "m1.small",
                    "InstanceCount": 1
                }
            ],
            "Ec2SubnetId": os.environ["EMR_EC2_SUBNET_ID"]
        },
        JobFlowRole=os.environ["EMR_EC2_DEFAULT_ROLE"],
        LogUri=os.environ["EMR_LOG_URI"],
        Name=os.environ["EMR_NAME"],
        ReleaseLabel="emr-6.6.0",
        #
        # Scale-down behavior options are no longer supported since Amazon EMR release version 5.10.0.
        # Because of the introduction of per-second billing in Amazon EC2,
        # the default scale-down behavior for Amazon EMR clusters is now terminate at task completion.
        #
        # ScaleDownBehavior="TERMINATE_AT_INSTANCE_HOUR",
        ServiceRole = os.environ["EMR_DEFAULT_ROLE"],
        VisibleToAllUsers = True
    )

    logger.debug(json.dumps(response))

    return {
        "JobFlowId" : response["JobFlowId"],
        "ClusterArn" : response["ClusterArn"],
        "Status" : "STARTING"
    }



def lambda_handler(event, context):
    if not is_emr_cluster_exists():
        return start_emr_cluster()

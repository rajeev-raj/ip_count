from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_ssm as ssm,
    core,
)

class EC2WithCloudWatchAgentStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an EC2 instance
        vpc = ec2.Vpc(self, "VPC", max_azs=2)
        instance = ec2.Instance(self, "EC2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            vpc=vpc
        )

        # Add IAM permissions to the instance
        instance.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy"))

        # Install the CloudWatch agent using SSM
        instance.user_data.add_commands(
            "sudo yum -y install amazon-cloudwatch-agent",
            "sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:/AmazonCloudWatch-linux -s",
        )

        # Create a CloudWatch Logs group
        log_group = logs.LogGroup(self, "CloudWatchLogsGroup", retention=logs.RetentionDays.ONE_WEEK)

        # Create the CloudWatch agent configuration using SSM
        ssm.StringParameter(self, "CloudWatchAgentConfigParameter",
            parameter_name="/AmazonCloudWatch-linux",
            string_value=f'''
                {{
                    "logs": {{
                        "logs_collected": {{
                            "files": {{
                                "collect_list": [
                                    {{
                                        "file_path": "/var/log/messages",
                                        "log_group_name": "{log_group.log_group_name}",
                                        "log_stream_name": "messages",
                                        "timestamp_format": "%b %d %H:%M:%S",
                                        "timezone": "LOCAL"
                                    }}
                                ]
                            }}
                        }}
                    }},
                    "metrics": {{
                        "metrics_collected": {{
                            "cpu": {{
                                "measurement": [
                                    "cpu_usage_idle",
                                    "cpu_usage_user",
                                    "cpu_usage_system"
                                ],
                                "metrics_collection_interval": 60,
                                "totalcpu": false
                            }},
                            "disk": {{
                                "measurement": [
                                    "used_percent"
                                ],
                                "metrics_collection_interval": 60,
                                "resources": [
                                    "*"
                                ]
                            }},
                            "mem": {{
                                "measurement": [
                                    "mem_used_percent"
                                ],
                                "metrics_collection_interval": 60
                            }}
                        }}
                    }}
                }}
            '''
        )


app = core.App()
EC2WithCloudWatchAgentStack(app, "EC2WithCloudWatchAgentStack")
app.synth()

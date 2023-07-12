from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
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
            vpc=vpc,
            user_data=ec2.UserData.custom(
                "#!/bin/bash\n"
                "yum -y install amazon-cloudwatch-agent\n"
                "cat <<EOF >> /opt/aws/amazon-cloudwatch-agent/bin/config.json\n"
                "{\n"
                '  "agent": {\n'
                '    "metrics_collection_interval": 60,\n'
                '    "run_as_user": "root"\n'
                '  },\n'
                '  "metrics": {\n'
                '    "metrics_collected": {\n'
                '      "cpu": {\n'
                '        "measurement": [\n'
                '          "cpu_usage_idle",\n'
                '          "cpu_usage_user",\n'
                '          "cpu_usage_system"\n'
                '        ],\n'
                '        "totalcpu": false\n'
                '      },\n'
                '      "disk": {\n'
                '        "measurement": [\n'
                '          "used_percent"\n'
                '        ],\n'
                '        "resources": [\n'
                '          "*"\n'
                '        ]\n'
                '      },\n'
                '      "mem": {\n'
                '        "measurement": [\n'
                '          "mem_used_percent"\n'
                '        ]\n'
                '      }\n'
                '    }\n'
                '  },\n'
                '  "logs": {\n'
                '    "logs_collected": {\n'
                '      "files": {\n'
                '        "collect_list": [\n'
                '          {\n'
                '            "file_path": "/var/log/messages",\n'
                '            "log_group_name": "/aws/ec2/instance",\n'
                '            "log_stream_name": "{instance_id}",\n'
                '            "timestamp_format": "%b %d %H:%M:%S",\n'
                '            "timezone": "LOCAL"\n'
                '          }\n'
                '        ]\n'
                '      }\n'
                '    }\n'
                '  }\n'
                '}\n'
                "EOF\n"
                "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a start\n"
            )
        )

        # Add IAM permissions to the instance
        instance.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy"))

        # Create a CloudWatch Logs group
        log_group = logs.LogGroup(self, "CloudWatchLogsGroup", retention=logs.RetentionDays.ONE_WEEK)
        log_group.grant_write(instance.role)

app = core.App()
EC2WithCloudWatchAgentStack(app, "EC2WithCloudWatchAgentStack")
app.synth()

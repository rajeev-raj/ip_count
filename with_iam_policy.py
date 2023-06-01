import boto3

# Create a Boto3 client for AWS Lambda and IAM
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')

# Define the IAM policy document for VPC readonly access
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:Get*",
                "ec2:List*"
            ],
            "Resource": "*"
        }
    ]
}

# Create the IAM policy
policy_response = iam_client.create_policy(
    PolicyName='VPCReadonlyAccessPolicy',
    PolicyDocument=str(policy_document),
    Description='Policy for VPC readonly access'
)

# Get the ARN of the created policy
policy_arn = policy_response['Policy']['Arn']

# Create the Lambda function
lambda_response = lambda_client.create_function(
    FunctionName='MyLambdaFunction',
    Runtime='python3.8',
    Role='arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ROLE_NAME',
    Handler='lambda_function.handler',
    Code={
        'ZipFile': open('lambda_function.zip', 'rb').read()  # Replace with your Lambda function code package
    },
    Description='My Lambda function',
    Timeout=300,
    MemorySize=128,
    Publish=True,
    VpcConfig={
        'SubnetIds': ['subnet-12345678', 'subnet-abcdefgh'],  # Replace with your subnet IDs
        'SecurityGroupIds': ['sg-12345678']  # Replace with your security group IDs
    },
    DeadLetterConfig={
        'Type': 'SNS',
        'TargetArn': 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:YOUR_SNS_TOPIC'  # Replace with your SNS topic ARN
    }
)

# Add the IAM policy to the Lambda function's execution role
iam_client.attach_role_policy(
    RoleName='YOUR_ROLE_NAME',  # Replace with your role name
    PolicyArn=policy_arn
)

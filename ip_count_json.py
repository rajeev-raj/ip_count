import boto3
import json

def count_ips_in_subnets():
    # Create a Boto3 client for EC2
    ec2_client = boto3.client('ec2')

    # Retrieve the list of subnets in the AWS account
    response = ec2_client.describe_subnets()

    subnet_list = response['Subnets']

    result = []
    for subnet in subnet_list:
        subnet_id = subnet['SubnetId']
        cidr_block = subnet['CidrBlock']

        # Calculate the number of IP addresses in the subnet
        ip_count = sum(1 for _ in ipaddress.ip_network(cidr_block))

        subnet_info = {
            'SubnetId': subnet_id,
            'CIDRBlock': cidr_block,
            'IPCount': ip_count
        }

        result.append(subnet_info)

    # Convert the result to JSON format
    json_result = json.dumps(result, indent=4)
    print(json_result)

count_ips_in_subnets()

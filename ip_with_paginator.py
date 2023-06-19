import boto3
import json

def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for item in page:
            yield item

def get_available_ip_addresses():
    ec2 = boto3.client('ec2')

    results = []

    # Retrieve all VPCs using pagination
    for vpc in paginate(ec2.describe_vpcs):
        vpc_id = vpc['VpcId']

        # Create a paginator for describing subnets within the VPC
        subnet_paginator = ec2.get_paginator('describe_subnets')

        # Paginate through the subnets within the VPC
        for subnet_page in subnet_paginator.paginate(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]):
            subnets = subnet_page['Subnets']

            # Iterate through each subnet
            for subnet in subnets:
                subnet_id = subnet['SubnetId']

                # Retrieve the available IP addresses for the subnet
                response = ec2.describe_subnet(SubnetIds=[subnet_id])
                available_ips = response['Subnets'][0]['AvailableIpAddressCount']

                # Check if available IPs are less than 10
                if available_ips < 10:
                    result = {
                        'vpc_id': vpc_id,
                        'subnet_id': subnet_id,
                        'available_count': available_ips
                    }
                    results.append(result)

    # Convert results to JSON
    json_output = json.dumps(results, indent=4)
    print(json_output)

# Call the function to get the available IP addresses less than 10 in JSON format
get_available_ip_addresses()

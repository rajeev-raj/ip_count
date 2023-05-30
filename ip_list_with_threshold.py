import json
import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    
    # Get all VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    
    result = []
    
    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        
        # Get all subnets in the VPC
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            
            # Get the IP count in the subnet
            ip_count = subnet['AvailableIpAddressCount']
            
            # Check if the IP count is less than 10
            if ip_count < 10:
                result.append({
                    'VpcId': vpc_id,
                    'SubnetId': subnet_id,
                    'IpCount': ip_count
                })
    
    # Return the result in JSON format
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

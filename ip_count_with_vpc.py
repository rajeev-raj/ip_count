import boto3
import json

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    
    # Get a list of all VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    
    result = []
    
    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        
        # Get a list of all subnets in the VPC
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        
        subnet_counts = []
        
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            
            # Get the IP count for the subnet
            ip_count = subnet['AvailableIpAddressCount']
            
            subnet_counts.append({
                'SubnetId': subnet_id,
                'IPCount': ip_count
            })
        
        result.append({
            'VpcId': vpc_id,
            'SubnetCounts': subnet_counts
        })
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

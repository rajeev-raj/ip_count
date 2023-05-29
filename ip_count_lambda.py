import boto3

def get_subnet_ip_counts():
    ec2_client = boto3.client('ec2')
    subnets = ec2_client.describe_subnets()['Subnets']
    
    subnet_ip_counts = {}
    
    for subnet in subnets:
        subnet_id = subnet['SubnetId']
        cidr_block = subnet['CidrBlock']
        
        ip_count = cidr_block.split('/')[1]
        subnet_ip_counts[subnet_id] = int(ip_count)
    
    return subnet_ip_counts

def lambda_handler(event, context):
    subnet_ip_counts = get_subnet_ip_counts()
    
    for subnet_id, ip_count in subnet_ip_counts.items():
        print(f"Subnet ID: {subnet_id} - IP Count: {ip_count}")

    return {
        'statusCode': 200,
        'body': 'Subnet IP counts calculated successfully.'
    }

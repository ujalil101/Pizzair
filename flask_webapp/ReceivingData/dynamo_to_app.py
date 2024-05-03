import boto3
from dotenv import load_dotenv
import os

load_dotenv()

# load keys from .env file
Access_Key = os.getenv("Access_Key")
Secret_Key = os.getenv("Secret_Key")

# connect to DynamoDB
session = boto3.Session(
    aws_access_key_id=Access_Key,
    aws_secret_access_key=Secret_Key,
    region_name="us-east-1"
)
dynamodb = session.client('dynamodb')


table_name = 'DataRetrieve'

# function to fetch data from dynamodb
def retrieve_data():
    try:
        response = dynamodb.scan(
            TableName=table_name
        )
        items = response['Items']
        
        # Sort items based on the timestamp in the Retrieve attribute
        sorted_items = sorted(items, key=lambda x: float(x['Retrieve']['S']))
        
        return sorted_items[-1]
    except Exception as e:
        print("Error fetching data from DynamoDB:", e)
        return []



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
        return response['Items']
    except Exception as e:
        print("Error fetching data from DynamoDB:", e)
        return []



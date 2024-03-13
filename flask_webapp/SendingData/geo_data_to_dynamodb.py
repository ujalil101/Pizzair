import boto3
from dotenv import load_dotenv
import os

load_dotenv()

# load keys from .env file
Access_Key = os.getenv("Access_Key")
Secret_Key = os.getenv("Secret_Key")

# connect to dyanomdb table
session = boto3.Session(
    aws_access_key_id=Access_Key,
    aws_secret_access_key=Secret_Key,
    region_name="us-east-1"
)
dynamodb = session.client('dynamodb')




def insert_into_dynamodb(starting_longitude, starting_latitude, destination_longitude, destination_latitude):
    try:
        session = boto3.Session(
            aws_access_key_id=Access_Key,
            aws_secret_access_key=Secret_Key,
            region_name="us-east-1"
        )
        dynamodb = session.client('dynamodb')

        table_name = 'Coordinates'
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'user_loc': {'S': 'Sending'},  
                'StartingLatitude': {'S': str(starting_latitude)},
                'StartingLongitude': {'S': str(starting_longitude)},
                'DestinationLatitude': {'S': str(destination_latitude)},
                'DestinationLongitude': {'S': str(destination_longitude)},
            }
        )
        print("Data inserted into DynamoDB:", response)

    except Exception as e:
        print("Error inserting data into DynamoDB:", e)



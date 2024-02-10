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


longitude = "42.3503911"
latitude = "-71.1027253"


# function to insert data to dynamodb table
def insert_into_dynamodb(longitude, latitude):
    try:
        # dynamodb table name
        table_name = 'Coordinates'

        # insert item into table
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'user_loc': {'S': 'Location'},  
                'Latitude': {'S': str(latitude)},  
                'Longitude': {'S': str(longitude)}  
            }
        )
        print("Data inserted into DynamoDB:", response)

    except Exception as e:
        print("Error inserting data into DynamoDB:", e)

print(insert_into_dynamodb(longitude, latitude))
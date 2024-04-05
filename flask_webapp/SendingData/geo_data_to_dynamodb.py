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


def insert_into_dynamodb(destination, destination_latitude, destination_longitude, delivery_boolean):
    try:
        table_name = 'Coordinates'
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'user_loc': {'S': 'Admin'}  # use  same key value to ensure one item
            },
            UpdateExpression='SET DestinationLatitude = :lat, DestinationLongitude = :lon, Deliver = :deliv',
            ExpressionAttributeValues={
                ':lat': {'S': str(destination_latitude)},
                ':lon': {'S': str(destination_longitude)},
                ':deliv': {'BOOL': delivery_boolean}
            },
            ReturnValues='ALL_NEW'  # return updated item after the update
        )
        print("Data updated in DynamoDB:", response)

    except Exception as e:
        print("Error updating data in DynamoDB:", e)


def update_delivery_status(delivery_status):
    try:
        table_name = 'Coordinates'
        key = {'user_loc': {'S': 'Admin'}}  # use same key value
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression='SET Deliver = :deliv',
            ExpressionAttributeValues={
                ':deliv': {'BOOL': delivery_status}
            },
            ReturnValues='UPDATED_NEW'  # return the updated item after the update
        )
        print("Delivery status updated in DynamoDB:", response)

    except Exception as e:
        print("Error updating delivery status in DynamoDB:", e)

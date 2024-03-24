import boto3
from dotenv import load_dotenv
import os
import time
table_name = 'DataRetrieve'
def initialize_jetson_to_dynamo():
    load_dotenv()

    # Load keys from .env file
    Access_Key = os.getenv("Access_Key")
    Secret_Key = os.getenv("Secret_Key")

    # Connect to DynamoDB
    session = boto3.Session(
        aws_access_key_id=Access_Key,
        aws_secret_access_key=Secret_Key,
        region_name="us-east-1"
    )
    dynamodb = session.client('dynamodb')

    
    return dynamodb


def insert_data(dynamodb, image_url, gps_coordinates, accelerometer_info, control_info):
    try:
        item = {
            'Retrieve': {'S': str(time.time())},  
            'Image': {'S': image_url},
            'GPS': {'M': gps_coordinates},
            'Accelerometer': {'M': accelerometer_info},
            'Control': {'M': control_info}
        }
        
        # Insert data
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        print("Data inserted into DynamoDB:", response)
    except Exception as e:
        print("Error inserting data into DynamoDB:", e)

# fake data
#image_url = 'https://cdn.mos.cms.futurecdn.net/76XArwuAqGZUGwffH2inpf-970-80.jpg'
#gps_coordinates = {'latitude': {'N': '37.7749'}, 'longitude': {'N': '-122.4194'}}
#accelerometer_info = {'x': {'N': '0.5'}, 'y': {'N': '0.3'}, 'z': {'N': '0.7'}}
#control_info = {
#    'mag': {'N': str(8)},      
#    'direction': {'S': str(8)},
#    'Safety': {'N': str(12)}   
#}
#dynamodb = initialize_jetson_to_dynamo()

#insert_data(dynamodb, image_url, gps_coordinates, accelerometer_info, control_info)

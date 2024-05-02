import boto3
from dotenv import load_dotenv
import os
table_name = 'Coordinates'


    
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
# function to fetch data from dynamodb
def fetch_coordinates_for_mapping():
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
    try:
        # fetch items
        response = dynamodb.scan(
            TableName=table_name
        )
        # print items
        #for item in response['Items']:
           # print(item) # this prints: {'DestinationLongitude': {'S': '42.3478109'}, 'StartingLatitude': {'S': '-71.1027253'}, 'user_loc': {'S': 'Sending'}, 'DestinationLatitude': {'S': '-71.1052321'}, 'StartingLongitude': {'S': '42.3503911'}}
        return response['Items'] # just specify what you want.  look at geodata to dyanmodb to see formating
    except Exception as e:
        print("Error fetching data from DynamoDB:", e)



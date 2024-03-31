import boto3
from dotenv import load_dotenv
import os

table_name = 'Coordinates'

def Retrieve_Coordinates():
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

    return dynamodb
    

# function to fetch data from DynamoDB
def fetch_from_dynamodb(dynamodb):
    try:
        # fetch items
        response = dynamodb.scan(TableName=table_name)
        
        # store combined data
        data = []

        # iterate through response items
        for item in response['Items']:
            combined_item = {
                'DestinationLatitude': item['DestinationLatitude']['S'],
                'DestinationLongitude': item['DestinationLongitude']['S'],
                'StartingLatitude': item['StartingLatitude']['S'],
                'StartingLongitude': item['StartingLongitude']['S']
                # Add other fields from the main table as needed
            }
            data.append(combined_item)

        
    except Exception as e:
        print("Error fetching data from DynamoDB:", e)
    starting_lat = data[0]['StartingLatitude']
    starting_lon = data[0]['StartingLongitude']
    dest_lat = data[0]['DestinationLatitude']
    dest_lon = data[0]['DestinationLongitude']
    return starting_lat,starting_lon, dest_lat,dest_lon

# call fetch function
dynamodb = Retrieve_Coordinates() 
fetch_from_dynamodb(dynamodb)

from flask import Flask, render_template, request, jsonify, redirect, url_for,session
from SendingData.geocoding import geocode_address
from dotenv import load_dotenv
from SendingData.geo_data_to_dynamodb import insert_into_dynamodb, update_delivery_status
from ReceivingData.dynamo_to_app import retrieve_data  

import boto3
import os
load_dotenv
app = Flask(__name__)

# api
google_maps_api_key = os.getenv("API_Key")
app.secret_key = os.environ.get('Secret_Key') 


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/geocode', methods=['POST'])
def geocode():
    data = request.get_json()
    destination_coordinates = geocode_address(google_maps_api_key, data['destination'])
    # update DynamoDB with delivery status
    insert_into_dynamodb(data['destination'], destination_coordinates[0], destination_coordinates[1], True)

    return jsonify({
        'destination': destination_coordinates
    })


@app.route('/submit_form', methods=['POST'])
def submit_form(): 
    return redirect(url_for('display_data'))

# This route will render the display_data.html page
@app.route('/display_data')
def display_data():
    # fetch data
    data = retrieve_data()

    # fetch coordinates
    '''
    
    dynamodb = Retrieve_Coordinates() 
    location = fetch_from_dynamodb(dynamodb)
    starting_lat = location[0]
    starting_lon = location[1]
    dest_lat = location[2]
    dest_lon = location[3]
    '''
    # pass data and API key
    return render_template('display_data.html', 
                           data=data)

# Stop/Start Flight option
@app.route('/update_delivery_status', methods=['POST'])
def update_delivery_status_route():
    data = request.get_json()
    delivery_status = data.get('deliveryStatus')  # get the new delivery status from request
    # update delivery status in Coordinates table
    update_delivery_status(delivery_status)
    return jsonify({'success': True})
    



                           
if __name__ == "__main__":
    app.run(debug=True)

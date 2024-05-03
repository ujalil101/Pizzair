from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from SendingData.geocoding import geocode_address
from SendingData.geo_data_to_dynamodb import insert_into_dynamodb, update_delivery_status
from SendingData.dynamodb_to_jetson import fetch_coordinates_for_mapping
from ReceivingData.dynamo_to_app import retrieve_data

import os

load_dotenv()
app = Flask(__name__)

# load API keys and secret key
google_maps_api_key = os.getenv("API_Key")
app.secret_key = os.environ.get('Secret_Key')

# route to retrieve data from DynamoDB
@app.route('/retrieve_data')
def retrieve_data_route():
    try:
        # Fetch data from DynamoDB
        data = retrieve_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

# route to fetch coordinates for mapping
@app.route('/fetch_coordinates')
def fetch_coordinates():
    try:
        # Fetch coordinates from DynamoDB
        coordinates = fetch_coordinates_for_mapping()
        return jsonify(coordinates)
    except Exception as e:
        return jsonify({'error': str(e)})


# route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# route to handle geocoding
@app.route('/geocode', methods=['POST'])
def geocode():
    data = request.get_json()
    start_coordinates = geocode_address(google_maps_api_key, data['start'])
    destination_coordinates = geocode_address(google_maps_api_key, data['destination'])
    
    # update DynamoDB with start and destination coordinates and delivery status
    insert_into_dynamodb(data['start'], start_coordinates[0], start_coordinates[1], data['destination'], destination_coordinates[0], destination_coordinates[1], True)

    return jsonify({'destination': destination_coordinates})

# route to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form(): 
    return redirect(url_for('display_data'))

# route to render the display_data.html page
@app.route('/display_data')
def display_data():
    # get data
    data = retrieve_data()

    # pass data to the display_data.html template
    return render_template('display_data.html', data=data)

# route to update delivery status
@app.route('/update_delivery_status', methods=['POST'])
def update_delivery_status_route():
    data = request.get_json()
    delivery_status = data.get('deliveryStatus')  # get the new delivery status from request
    # update delivery status in Coordinates table
    update_delivery_status(delivery_status)
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True)


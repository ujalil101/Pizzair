from flask import Flask, render_template, request, jsonify, redirect, url_for
from SendingData.geocoding import geocode_address
from dotenv import load_dotenv
from SendingData.geo_data_to_dynamodb import insert_into_dynamodb
from ReceivingData.dynamo_to_app import retrieve_data  # Importing retrieve_data function from your script
import boto3
import os
load_dotenv
app = Flask(__name__)

# api
google_maps_api_key = os.getenv("API_Key")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/geocode', methods=['POST'])
def geocode():
    data = request.get_json()
    
    
    starting_point_coordinates = geocode_address(google_maps_api_key, data['startingPoint'])

    destination_coordinates = geocode_address(google_maps_api_key, data['destination'])
   

    #  insert data into dyanmodb

    insert_into_dynamodb(starting_point_coordinates[0], starting_point_coordinates[1], 
                         destination_coordinates[0], destination_coordinates[1])

    return jsonify({
        'startingPoint': starting_point_coordinates,
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
    if data:
        return render_template('display_data.html', data=data)
    else:
        return "No data available"  



                           
if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for
from geocoding import geocode_address
from dotenv import load_dotenv
from geo_data_to_dynamodb import insert_into_dynamodb
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
    print(starting_point_coordinates)
    destination_coordinates = geocode_address(google_maps_api_key, data['destination'])
    #print(starting_point_coordinates[0])
    #print(destination_coordinates[1])

    # Call the function to insert data into DynamoDB

    insert_into_dynamodb(starting_point_coordinates[0], starting_point_coordinates[1])
   # insert_into_dynamodb(destination_coordinates[0], destination_coordinates[1])

    return jsonify({
        'startingPoint': starting_point_coordinates,
        'destination': destination_coordinates
    })
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Process the form data as needed
    # For now, let's just redirect to display_data.html
    return redirect(url_for('display_data'))

# This route will render the display_data.html page
@app.route('/display_data')
def display_data():
    return render_template('display_data.html')
if __name__ == "__main__":
    app.run(debug=True)

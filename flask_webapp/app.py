from flask import Flask, render_template, request, jsonify
from geocoding import geocode_address
from dotenv import load_dotenv
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

    # call geocoding function to get coordiantes for starting point
    starting_point_coordinates = geocode_address(google_maps_api_key, data['startingPoint'])
    # call geocoding function to get coordiantes for destination point
    destination_coordinates = geocode_address(google_maps_api_key, data['destination'])

    print(starting_point_coordinates, destination_coordinates)
    return jsonify({
        'startingPoint': starting_point_coordinates,
        'destination': destination_coordinates
    })


if __name__ == "__main__":
    app.run(debug=True)

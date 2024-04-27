# Overall Software Architecture Diagram 

![Screenshot 2023-12-07 at 10 19 03 PM](https://github.com/ujalil101/Pizzair/assets/74789609/05af49bf-c516-4dab-9576-6987fccf92e7)


## Software Architecture Diagram: Web App and Jetson Nano
![Screenshot 2024-01-29 at 5 21 03 PM](https://github.com/ujalil101/Pizzair/assets/74789609/3666eff7-9087-4d4c-97e7-82f90717066e)


## Software Architecture Diagram: DynamoDB tables
![Screenshot 2024-03-14 at 2 26 28 AM](https://github.com/ujalil101/Pizzair/assets/74789609/fa2fb48e-f40e-4d61-91a3-ac58fd963f26)

# Frontend

### display_data.html
This HTML file is a template for displaying data retrieved from a Jetson Nano device. It includes sections for displaying images, GPS coordinates, accelerometer info, and control data. Additionally, it integrates with the Leaflet library for displaying a map and periodically fetches data from the server using JavaScript.

### index.html 
This HTML file serves as a user interface which allows users to enter a destination address and sends a POST request to a geocoding endpoint `/geocode` with the entered destination. If successful, it redirects the user to another page to display the data.

# Modules

### dynamo_to_app.py
This module facilitates data retrieval from the `DataRetreive` table for Python applications. It handles AWS configuration and interaction complexities, providing a simple interface for fetching data.

### jetson_to_dynamo.py
The `jetson_to_dynamo.py` module streamlines the process of inserting data into the `DataRetrieval` table from a Jetson Nano device. It manages the necessary AWS configurations and interaction logic, simplifying data insertion tasks.

### dynamodb_to_jetson.py
The `dynamodb_to_jetson.py` module offers functionality for fetching data from DynamoDB. It handles the AWS configurations and interaction logic, providing a straightforward way to retrieve data from DynamoDB tables.

### geo_data_to_dynamodb.py
The `geo_data_to_dynamodb.py` module simplifies the process of inserting coordinates into the `Coordinates` table. It handles AWS configurations and interaction logic, making it easy to add geospatial data to DynamoDB.

### geocoding.py
The `geocoding.py` module utilizes the Google Maps API to convert addresses to longitude and latitude coordinates. It provides a convenient way to integrate geocoding functionality into applications.


# Routes and Endpoints

The app.py flask application defines several routes and endpoints to handle different types of requests:
- `/retrieve_data`: Retrieves data from DynamoDB and returns it as JSON.
- `/`: Renders the `index.html` page.
- `/geocode`: Handles geocoding requests, converting addresses to coordinates and updating DynamoDB.
- `/submit_form`: Redirects to the `display_data` route after form submission.
- `/display_data`: Renders the `display_data.html` page and passes retrieved data to it.
- `/update_delivery_status`: Updates delivery status in DynamoDB based on the request data.

# Module Flow Chart
![Screenshot 2024-04-26 at 9 55 54 PM](https://github.com/ujalil101/Pizzair/assets/74789609/1399cbd6-457a-4863-9a34-f5cd1c085618)


# Installation Prerequsites
## Google Maps
1. **Sign in to Google Cloud Console**
Log in to your Google Cloud Console
2. **Create a New Project**
Click on the "Select a project" dropdown and choose "New Project"
3. **Create API Key**
- In the Google Cloud Console, navigate to the `APIs & Services` > `Credentials` section
- Click on the `Create credentials` dropdown and select "API key"
- Copy the API key
## AWS
1. **Sign in to AWS Console**
Log in to your AWS Management Console
2. **Open DynamoDB Console**
Navigate to the DynamoDB service.
3. **Create Table**
- Click on "Create table"
- Enter "Coordiantes" for the table name
- Click "Create"
4. **Repeat for Additional Tables**
- Do the same for "DataRetreive" table

# Installation for Flask Web App

1. **Clone the Repository:**
```
git clone <repository_url>
```
2. **Navigate to  Web App Directory**
```
cd flask_webapp
```
3. **Install Dependencies**
```
pip install -r requirements.txt
```
4. **Set Up Environment Variables**
- create a google maps API key
- create an AWS Access Key and Secret Key
- create a .env file and add these keys as followed:
   ```
    API_Key = ""
    Access_Key = ""
    Secret_Key = ""
    ```
5. **Run the App**
```
python3 app.py
```
6. **Access the App**
After running the app, you can access the application in your web browser by navigating to the specified URL `http://localhost:5000/` 
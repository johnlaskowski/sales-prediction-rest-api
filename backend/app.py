# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
sales_predictor_api = Flask("SuperKart Price Predictor")

# Load the trained machine learning model
model = joblib.load("SuperKart_prediction_model_v1_0.joblib")

# Define a route for the home page (GET request)
@sales_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Prediction API!"

# Define an endpoint for single sales prediction (POST request)
@sales_predictor_api.post('/v1/sale')
def predict_sales():
    """
    This function handles POST requests to the '/v1/sale' endpoint.
    It expects a JSON payload containing product details and returns
    the predicted sales amount as a JSON response.
    """
    # Get the JSON data from the request body
    product_data = request.get_json(force=True) or {}

    # Support both snake_case and legacy DataFrame-style keys
    sample = {
        'Product_Weight': product_data.get('product_weight', product_data.get('Product_Weight')),
        'Product_Type': product_data.get('product_type', product_data.get('Product_Type')),
        'Product_MRP': product_data.get('product_mrp', product_data.get('Product_MRP')),
        'Store_Size': product_data.get('store_size', product_data.get('Store_Size')),
        'Store_Location_City_Type': product_data.get('store_location_city_type', product_data.get('Store_Location_City_Type')),
        'Store_Type': product_data.get('store_type', product_data.get('Store_Type'))
    }

    missing_fields = [key for key, value in sample.items() if value is None]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction (get sales)
    predicted_sales = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    predicted_sales = round(float(predicted_sales), 2)
    # The conversion above is needed as we convert the model prediction (log price) to actual price using np.exp, which returns predictions as NumPy float32 values.
    # When we send this value directly within a JSON response, Flask's jsonify function encounters a datatype error

    # Return the actual price
    return jsonify({'Predicted sales (in dollars)': predicted_sales})


# Define an endpoint for batch prediction (POST request)
@sales_predictor_api.post('/v1/salebatch')
def predict_sales_batch():
    """
    This function handles POST requests to the '/v1/salebatch' endpoint.
    It expects a CSV file containing product details for multiple products
    and returns predicted sales in a dictionary keyed by product ID when available.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all properties in the DataFrame
    predicted_sales = [round(float(p), 2) for p in model.predict(input_data).tolist()]

    # Use Product_Id when available; otherwise fall back to row numbers
    product_id_column = next((col for col in ['Product_Id', 'Product_ID', 'id'] if col in input_data.columns), None)
    if product_id_column is not None:
        product_ids = input_data[product_id_column].tolist()
        return dict(zip(product_ids, predicted_sales))

    return {'predictions': predicted_sales}

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    sales_predictor_api.run(debug=True, port=7860)

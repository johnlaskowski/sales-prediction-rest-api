import os
import streamlit as st
import pandas as pd
import requests

# Use Docker service name inside Compose, but allow localhost for local runs
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:7860")

# Set the title of the Streamlit app
st.title("SuperKart Sales Prediction")

# Section for online prediction
st.subheader("Online Sales Prediction")

# Collect user input for property features
product_weight = st.number_input("Product Weight?", min_value=1, step=1, value=13)
product_type = st.selectbox(
    "Product Type?",
    ["Fruits and Vegetables", "Snack Foods", "Frozen Foods", "Dairy",
     "Household", "Baking Goods", "Canned", "Health and Hygiene", "Meat",
     "Soft Drinks", "Breads", "Hard Drinks", "Others", "Starchy Foods",
     "Breakfast", "Seafood"]
)
product_mrp = st.number_input("Maximum Retail Price?", min_value=0.0, max_value=1000.0, step=1.0, value=145.0)
store_size = st.selectbox("Store Size?", ["Small", "Medium", "High"])
store_location_city_type = st.selectbox("City Type?", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type?", ["Food Mart", "Departmental Store", "Supermarket Type1", "Supermarket Type2"])

# Build a payload that matches the backend contract
payload = {
    'product_weight': product_weight,
    'product_type': product_type,
    'product_mrp': product_mrp,
    'store_size': store_size,
    'store_location_city_type': store_location_city_type,
    'store_type': store_type
}

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    response = requests.post(
        f"{BACKEND_URL}/v1/sale",
        json=payload,
        timeout=30
    )
    if response.status_code == 200:
        prediction = response.json()['Predicted sales (in dollars)']
        st.success(f"Predicted sales(in dollars): {prediction}")
    else:
        st.error("Unable to connect to the prediction API.")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        response = requests.post(
            f"{BACKEND_URL}/v1/salebatch",
            files={"file": uploaded_file}
        )
        if response.status_code == 200:
            predictions = response.json()
            st.success("Batch predictions completed!")
            st.write(predictions)
        else:
            st.error("Unable to connect to the prediction API.")

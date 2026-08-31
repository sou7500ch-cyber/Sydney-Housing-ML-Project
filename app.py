import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load trained model and feature structure
model = joblib.load("sydney_housing_random_forest.pkl")
model_features = joblib.load("model_features.pkl")

# Page configuration
st.set_page_config(
    page_title="Sydney Housing Price Predictor",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Sydney Housing Price Predictor")
st.write(
    "Enter the property details below to estimate the sale price "
    "using the trained Random Forest model."
)

# User inputs
suburb = st.selectbox(
    "Suburb",
    ["Blacktown", "Chatswood", "Parramatta"]
)

land_size = st.number_input(
    "Land Size (m²)",
    min_value=1.0,
    value=170.0,
    step=1.0
)

contract_year = st.number_input(
    "Contract Year",
    min_value=2022,
    max_value=2030,
    value=2026,
    step=1
)

contract_month = st.selectbox(
    "Contract Month",
    list(range(1, 13)),
    index=6
)

zoning = st.selectbox(
    "Zoning",
    ["", "C4", "E4", "R1", "R2"]
)

# Prediction button
if st.button("Predict Sale Price"):

    # Create input data
    input_data = {
        "Land Size": land_size,
        "Contract_Year": contract_year,
        "Contract_Month": contract_month,
        "Log_Land_Size": np.log1p(land_size),
        "Suburb_Blacktown": 1.0 if suburb == "Blacktown" else 0.0,
        "Suburb_Chatswood": 1.0 if suburb == "Chatswood" else 0.0,
        "Suburb_Parramatta": 1.0 if suburb == "Parramatta" else 0.0,
        "Zoning_C4": 1.0 if zoning == "C4" else 0.0,
        "Zoning_E4": 1.0 if zoning == "E4" else 0.0,
        "Zoning_R1": 1.0 if zoning == "R1" else 0.0,
        "Zoning_R2": 1.0 if zoning == "R2" else 0.0
    }

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])

    # Ensure exact same feature order as training
    input_df = input_df[model_features]

    # Generate prediction
    prediction = model.predict(input_df)[0]

    # Display result
    st.success(
        f"Estimated Sale Price: ${prediction:,.0f}"
    )

    st.info(
        "This prediction is an estimate based on the properties "
        "and features used to train the model."
    )

import streamlit as st
import pandas as pd
import numpy as np
import joblib

from database import (
    initialise_database,
    create_property,
    get_all_properties,
    get_property,
    update_property,
    delete_property
)

# Initialise database
initialise_database()

# Load trained model and feature structure
model = joblib.load("sydney_housing_random_forest.pkl")
model_features = joblib.load("model_features.pkl")

# Page configuration
st.set_page_config(
    page_title="Sydney Housing Management System",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Sydney Housing Price Prediction & Management System")

st.write(
    "Predict Sydney property prices using the trained Random Forest model "
    "and manage property records using a SQLite database."
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Price Prediction",
        "Property Management"
    ]
)


# ============================================================
# PRICE PREDICTION
# ============================================================

if page == "Price Prediction":

    st.header("💰 Sydney Housing Price Prediction")

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

    if st.button("Predict Sale Price"):

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

        input_df = pd.DataFrame([input_data])

        # Ensure exact same feature order as training
        input_df = input_df[model_features]

        # Generate prediction
        prediction = model.predict(input_df)[0]

        st.success(
            f"Estimated Sale Price: ${prediction:,.0f}"
        )

        st.info(
            "This prediction is an estimate based on the properties "
            "and features used to train the model."
        )


# ============================================================
# PROPERTY MANAGEMENT / CRUD
# ============================================================

elif page == "Property Management":

    st.header("🏘️ Property Management")

    crud_operation = st.selectbox(
        "Select Operation",
        [
            "Add Property",
            "View Properties",
            "Update Property",
            "Delete Property"
        ]
    )


    # ========================================================
    # CREATE
    # ========================================================

    if crud_operation == "Add Property":

        st.subheader("➕ Add New Property")

        with st.form("create_property_form"):

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

            contract_month = st.number_input(
                "Contract Month",
                min_value=1,
                max_value=12,
                value=9,
                step=1
            )

            zoning = st.selectbox(
                "Zoning",
                ["C4", "E4", "R1", "R2"]
            )

            submitted = st.form_submit_button("Add Property")

            if submitted:

                property_id = create_property(
                    suburb,
                    land_size,
                    contract_year,
                    contract_month,
                    zoning
                )

                st.success(
                    f"Property added successfully. Property ID: {property_id}"
                )


    # ========================================================
    # READ
    # ========================================================

    elif crud_operation == "View Properties":

        st.subheader("📋 Property Records")

        properties = get_all_properties()

        if properties:

            columns = [
                "ID",
                "Suburb",
                "Land Size",
                "Contract Year",
                "Contract Month",
                "Zoning",
                "Created At"
            ]

            dataframe = pd.DataFrame(
                properties,
                columns=columns
            )

            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No property records found.")


    # ========================================================
    # UPDATE
    # ========================================================

    elif crud_operation == "Update Property":

        st.subheader("✏️ Update Property")

        properties = get_all_properties()

        if properties:

            property_ids = [
                property_record[0]
                for property_record in properties
            ]

            selected_id = st.selectbox(
                "Select Property ID",
                property_ids
            )

            property_record = get_property(selected_id)

            if property_record:

                with st.form("update_property_form"):

                    suburb = st.selectbox(
                        "Suburb",
                        ["Blacktown", "Chatswood", "Parramatta"],
                        index=[
                            "Blacktown",
                            "Chatswood",
                            "Parramatta"
                        ].index(property_record[1])
                    )

                    land_size = st.number_input(
                        "Land Size (m²)",
                        min_value=1.0,
                        value=float(property_record[2]),
                        step=1.0
                    )

                    contract_year = st.number_input(
                        "Contract Year",
                        min_value=2022,
                        max_value=2030,
                        value=int(property_record[3]),
                        step=1
                    )

                    contract_month = st.number_input(
                        "Contract Month",
                        min_value=1,
                        max_value=12,
                        value=int(property_record[4]),
                        step=1
                    )

                    zoning_options = ["C4", "E4", "R1", "R2"]

                    zoning = st.selectbox(
                        "Zoning",
                        zoning_options,
                        index=zoning_options.index(property_record[5])
                    )

                    submitted = st.form_submit_button(
                        "Update Property"
                    )

                    if submitted:

                        rows_updated = update_property(
                            selected_id,
                            suburb,
                            land_size,
                            contract_year,
                            contract_month,
                            zoning
                        )

                        if rows_updated:

                            st.success(
                                f"Property ID {selected_id} updated successfully."
                            )

                        else:

                            st.error(
                                "Property could not be updated."
                            )

        else:

            st.info("No property records available to update.")


    # ========================================================
    # DELETE
    # ========================================================

    elif crud_operation == "Delete Property":

        st.subheader("🗑️ Delete Property")

        properties = get_all_properties()

        if properties:

            property_ids = [
                property_record[0]
                for property_record in properties
            ]

            selected_id = st.selectbox(
                "Select Property ID",
                property_ids
            )

            property_record = get_property(selected_id)

            if property_record:

                st.write(
                    f"**Suburb:** {property_record[1]}"
                )

                st.write(
                    f"**Land Size:** {property_record[2]} m²"
                )

                st.write(
                    f"**Contract Year:** {property_record[3]}"
                )

                st.write(
                    f"**Contract Month:** {property_record[4]}"
                )

                st.write(
                    f"**Zoning:** {property_record[5]}"
                )

                if st.button(
                    "Delete Property",
                    type="primary"
                ):

                    rows_deleted = delete_property(
                        selected_id
                    )

                    if rows_deleted:

                        st.success(
                            f"Property ID {selected_id} deleted successfully."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Property could not be deleted."
                        )

        else:

            st.info("No property records available to delete.")
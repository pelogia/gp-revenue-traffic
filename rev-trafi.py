# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Streamlit app title
st.title("Traffic and Revenue Overlap with Enhanced Error Handling")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a CSV file with 'url', 'traffic', and 'revenue' columns.",
    type=['csv']
)

if uploaded_file:
    try:
        # Load CSV into a DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Check if required columns are present
        required_columns = ['url', 'traffic', 'revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Column(s) missing: {', '.join(missing_columns)}")
            st.stop()

        # Check for empty cells in required columns
        for col in required_columns:
            empty_cells = df[df[col].isnull()].index.tolist()
            if empty_cells:
                st.error(f"Missing values in column '{col}' at rows: {', '.join(map(str, empty_cells))}")
                st.stop()

        # Check if 'traffic' and 'revenue' columns contain only numeric values
        for col in ['traffic', 'revenue']:
            non_numeric = df[~df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notnull()].index.tolist()
            if non_numeric:
                st.error(f"Non-numeric values in column '{col}' at rows: {', '.join(map(str, non_numeric))}")
                st.stop()

        # Ensure the file is not empty
        if df.empty:
            st.error("The uploaded file is empty. Please upload a valid file with data.")
            st.stop()

        # Priority selection
        priority = st.radio("Select the priority for grouping:", ('Revenue', 'Traffic'))

        # Sort DataFrame based on priority
        if priority == 'Revenue':
            df_sorted = df.sort_values(by='revenue', ascending=False).reset_index(drop=True)
        else:
            df_sorted = df.sort_values(by='traffic', ascending=False).reset_index(drop=True)

        # Calculate cumulative revenue and traffic percentages
        total_revenue = df_sorted['revenue'].sum()
        total_traffic = df_sorted['traffic'].sum()
        df_sorted['cumulative_revenue'] = df_sorted['revenue'].cumsum() / total_revenue * 100
        df_sorted['cumulative_traffic'] = df_sorted['traffic'].cumsum() / total_traffic * 100

        # Grouping and visualization logic...
        st.write("Processing successful!")

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    st.info("Please upload a CSV file to proceed.")


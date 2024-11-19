# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Step 1: Streamlit app title
st.title("Traffic and Revenue Overlap")

# Step 2: Upload CSV file
uploaded_file = st.file_uploader(
    "Upload a CSV file with 'url', 'traffic', and 'revenue' columns. Below you'll find the summary by coverage groups (20/40/70/80%) and the export will have all specific pages split by group.",
    type=['csv']
)

if uploaded_file:
    try:
        # Step 3: Load the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Step 4: Error handling - Check if required columns are present
        required_columns = ['url', 'traffic', 'revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Column(s) missing: {', '.join(missing_columns)}")
            st.stop()

        # Step 5: Error handling - Check for empty cells
        for col in required_columns:
            empty_cells = df[df[col].isnull()].index.tolist()
            if empty_cells:
                st.error(f"Missing values in column '{col}' at rows: {', '.join(map(str, empty_cells))}")
                st.stop()

        # Step 6: Error handling - Check if 'traffic' and 'revenue' contain numeric values
        for col in ['traffic', 'revenue']:
            non_numeric = df[~df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).notnull()].index.tolist()
            if non_numeric:
                st.error(f"Non-numeric values in column '{col}' at rows: {', '.join(map(str, non_numeric))}")
                st.stop()

        # Step 7: Error handling - Ensure the file is not empty
        if df.empty:
            st.error("The uploaded file is empty. Please upload a valid file with data.")
            st.stop()

        # Step 8: User selects priority
        priority = st.radio("Select the priority for grouping:", ('Revenue', 'Traffic'))

        # Step 9: Sort the DataFrame based on the selected priority
        if priority == 'Revenue':
            df_sorted = df.sort_values(by='revenue', ascending=False).reset_index(drop=True)
        else:
            df_sorted = df.sort_values(by='traffic', ascending=False).reset_index(drop=True)

        # Step 10: Calculate cumulative revenue and traffic percentages
        total_revenue = df_sorted['revenue'].sum()
        total_traffic = df_sorted['traffic'].sum()
        df_sorted['cumulative_revenue'] = df_sorted['revenue'].cumsum() / total_revenue * 100
        df_sorted['cumulative_traffic'] = df_sorted['traffic'].cumsum() / total_traffic * 100

        # Step 11: Create coverage groups aiming for balanced percentages
        percentages = [20, 40, 60, 80, 100]
        all_data = []
        overview_data = []

        for percentage in percentages:
            # Select rows that balance traffic and revenue to approximate the percentage
            balanced_group = df_sorted[
                (df_sorted['cumulative_revenue'] <= percentage) |
                (df_sorted['cumulative_traffic'] <= percentage)
            ]

            # Add the next row if not reaching the threshold exactly
            if not balanced_group.empty and balanced_group.shape[0] < df_sorted.shape[0]:
                balanced_group = pd.concat([balanced_group, df_sorted.iloc[[balanced_group.shape[0]]]])

            # Calculate final percentages for this group
            final_revenue = balanced_group['revenue'].sum()
            final_traffic = balanced_group['traffic'].sum()
            num_pages = balanced_group.shape[0]

            # Add to overview
            overview_data.append({
                'Coverage': f"First {percentage}%",
                'Nr. Pages': num_pages,
                'Exact Revenue': f"{final_revenue / total_revenue * 100:.2f}%",
                'Exact Traffic': f"{final_traffic / total_traffic * 100:.2f}%"
            })

            # Add group data to final dataset
            balanced_group['Sheet'] = f'Top_{percentage}_Percent'
            all_data.append(balanced_group[['url', 'traffic', 'revenue', 'cumulative_traffic', 'cumulative_revenue', 'Sheet']])

        # Combine all groups into one DataFrame
        combined_data_df = pd.concat(all_data, ignore_index=True)

        # Step 12: Display the overview table
        st.subheader("Overview of Balanced Traffic and Revenue Percentages")
        overview_df = pd.DataFrame(overview_data)
        st.write(overview_df)

        # Step 13: Plot a graph for traffic and revenue percentages
        st.subheader("Traffic and Revenue Percentages by Coverage Group")
        fig, ax = plt.subplots()
        x_labels = overview_df['Coverage']
        traffic_percents = overview_df['Exact Traffic'].str.rstrip('%').astype(float)
        revenue_percents = overview_df['Exact Revenue'].str.rstrip('%').astype(float)

        ax.plot(x_labels, traffic_percents, marker='o', label='Traffic (%)')
        ax.plot(x_labels, revenue_percents, marker='o', label='Revenue (%)')
        ax.set_xlabel('Coverage Groups')
        ax.set_ylabel('Percentage')
        ax.set_title('Traffic vs Revenue by Coverage')
        ax.legend()

        st.pyplot(fig)

        # Step 14: Download the combined CSV
        output_file = combined_data_df.to_csv(index=False)
        st.download_button(
            label="Download Combined Analysis CSV",
            data=output_file,
            file_name="traffic_revenue_analysis.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

else:
    st.info("Please upload a CSV file to proceed.")

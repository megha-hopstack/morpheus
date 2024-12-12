#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 18:11:46 2024

@author: megha
"""

import streamlit as st
import pandas as pd
from collections import defaultdict
import ast

# Streamlit App
def main():
    st.title("Morpheus")
    st.write("Upload an Excel file containing order data.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        # Read the uploaded file into a DataFrame
        df = pd.read_excel(uploaded_file)
        # Ensure 'skus' column is properly parsed
        df['skus'] = df['skus'].apply(ast.literal_eval)
                # Exploding the SKUs
        df_exploded = df.explode('skus').reset_index(drop=True)

        # Normalize the 'skus' column into separate 'sku' and 'quantity' columns
        df_exploded['sku'] = df_exploded['skus'].apply(lambda x: x['sku'])
        df_exploded['quantity'] = df_exploded['skus'].apply(lambda x: x['qty'])

        # Track the original SKUs (before exploding) for grouping
        df['original_skus'] = df['skus'].apply(lambda x: [item['sku'] for item in x])

        # Drop 'skus' from exploded df now
        df_exploded = df_exploded.drop(columns=['skus'])

        st.subheader("Orders")
        st.dataframe(df_exploded)

        # ---------------------------------------------------
        # Step 1: Create Data Structures A and B
        # ---------------------------------------------------
        A = defaultdict(list)
        B = defaultdict(list)

        for _, row in df.iterrows():
            if len(row['original_skus']) == 1:
                sku = row['original_skus'][0]
                quantity = row['skus'][0]['qty']
                A[(sku, quantity)].append(row['_id'])
            elif len(row['original_skus']) == 2:
                skus = tuple(sorted([item['sku'] for item in row['skus']]))
                quantities = tuple([item['qty'] for item in row['skus']])
                B[(skus, quantities)].append(row['_id'])

        # Function to process and print the presets
        def display_presets(A, B, df):
            grouped_orders = set()
            results = []

            for key, order_ids in A.items():
                if len(order_ids) > 1:
                    grouped_orders.update(order_ids)
                    results.append(f"Orders having the same SKU and same quantities - {order_ids}")

            sku_quantity_groups = defaultdict(list)
            for key, order_ids in A.items():
                sku, quantity = key
                sku_quantity_groups[sku].append(quantity)

            for sku, quantities in sku_quantity_groups.items():
                if len(set(quantities)) > 1:
                    orders_with_diff_quantities = []
                    for (sku_check, qty), order_ids in A.items():
                        if sku_check == sku and qty in quantities:
                            grouped_orders.update(order_ids)
                            orders_with_diff_quantities.extend(order_ids)
                    results.append(f"Orders having the same SKU but may differ in quantities - {orders_with_diff_quantities}")

            for (skus, quantities), order_ids in B.items():
                if len(order_ids) > 1:
                    grouped_orders.update(order_ids)
                    results.append(f"Orders with same SKUs and matching quantities for both - {order_ids}")

            sku_pair_groups = defaultdict(list)
            for (skus, quantities), order_ids in B.items():
                sku_pair_groups[skus].extend(order_ids)

            for sku_pair, order_ids in sku_pair_groups.items():
                if len(order_ids) > 1:
                    grouped_orders.update(order_ids)
                    results.append(f"Orders with same SKUs but different quantities for at least one SKU - {order_ids}")

            sku_groups = defaultdict(list)
            for (sku, qty), order_ids in A.items():
                sku_groups[sku].extend(order_ids)

            for (skus, quantities), order_ids in B.items():
                for sku in skus:
                    sku_groups[sku].extend(order_ids)

            for sku, order_ids in sku_groups.items():
                if len(order_ids) > 1:
                    grouped_orders.update(order_ids)
                    results.append(f"Orders with SKU {sku} - {order_ids}")

            all_orders = set(df['_id'])
            miscellaneous_orders = all_orders - grouped_orders

            if miscellaneous_orders:
                results.append(f"Miscellaneous Orders - {sorted(list(miscellaneous_orders))}")

            city_groups = defaultdict(list)
            for _, row in df.iterrows():
                city_groups[row['city']].append(row['_id'])

            for city, order_ids in city_groups.items():
                if len(order_ids) > 1:
                    results.append(f"City: {city} - {order_ids}")

            state_groups = defaultdict(list)
            for _, row in df.iterrows():
                state_groups[row['state']].append(row['_id'])

            for state, order_ids in state_groups.items():
                if len(order_ids) > 1:
                    results.append(f"State: {state} - {order_ids}")

            country_groups = defaultdict(list)
            for _, row in df.iterrows():
                country_groups[row['country']].append(row['_id'])

            for country, order_ids in country_groups.items():
                if len(order_ids) > 1:
                    results.append(f"Country: {country} - {order_ids}")

            carrier_groups = defaultdict(list)
            for _, row in df.iterrows():
                carrier_groups[row['carrier']].append(row['_id'])

            for carrier, order_ids in carrier_groups.items():
                if len(order_ids) > 1:
                    results.append(f"Carrier: {carrier} - {order_ids}")

            return results

        presets = display_presets(A, B, df)
        st.subheader("Results")
        for preset in presets:
            st.write(preset)

if __name__ == "__main__":
    main()

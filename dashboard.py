import pandas as pd
import streamlit as st

# Load dataset
df = pd.read_csv('healthy_foods_dataset_final2.csv')

def segmented_budget_recommendations(total_budget, categories, sets=3):
    # Budgets decreasing slightly per set (95%, 92.5%, 90%, etc.)
    budgets = [
        total_budget * (1 - i * 0.025)  # example percentages, tweak if desired
        for i in range(sets)
    ]

    all_recommendations = []
    used_items = set()

    for budget in budgets:
        filtered = df[~df['Food Item'].isin(used_items) & df['Category'].isin(categories)].copy()
        price_column = 'Price_HalfKG (₹/kg)'
        filtered['nutrient_score'] = (filtered['Protein (g)'] + filtered['Fiber (g)']) / filtered[price_column]
        filtered = filtered.sort_values(by='nutrient_score', ascending=False)

        selected_rows = []
        total_cost = 0
        total_protein = 0
        total_fiber = 0

        for idx, row in filtered.iterrows():
            cost = row[price_column]
            if total_cost + cost <= budget:
                selected_rows.append(row)
                total_cost += cost
                total_protein += row['Protein (g)'] / 2  # half kg nutrition approximation
                total_fiber += row['Fiber (g)'] / 2
                used_items.add(row['Food Item'])

        recommended_df = pd.DataFrame(selected_rows)
        all_recommendations.append({
            'budget': budget,
            'dataframe': recommended_df,
            'total_cost': total_cost,
            'total_protein': total_protein,
            'total_fiber': total_fiber,
        })

    return all_recommendations

# Streamlit UI

st.title('Healthy Food Recommendation Based on Budget')

st.markdown("""
Welcome! This app helps you find healthy food sets within your budget using half-kilogram pricing.
Select your preferred food categories and budget to see optimized nutritious sets.
""")

budget = st.number_input('Enter your budget (₹)', min_value=1, value=1000)
categories = st.multiselect('Select Food Categories', options=df['Category'].unique())

if st.button('Get Recommendations'):
    if not categories:
        st.warning('Please select at least one food category.')
    else:
        recs = segmented_budget_recommendations(budget, categories, sets=3)
        for i, rec in enumerate(recs, 1):
            st.subheader(f'Set {i} - Budget allocated: ₹{rec["budget"]:.2f}')
            if not rec['dataframe'].empty:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Cost (₹)", f"{rec['total_cost']:.2f}")
                col2.metric("Total Protein (g)", f"{rec['total_protein']:.2f}")
                col3.metric("Total Fiber (g)", f"{rec['total_fiber']:.2f}")

                st.dataframe(rec['dataframe'][['Food Item', 'Category', 'Price_HalfKG (₹/kg)', 'Protein (g)', 'Fiber (g)', 'Calories']].style.format({
                    'Price_HalfKG (₹/kg)': '₹{:.2f}',
                    'Protein (g)': '{:.2f}',
                    'Fiber (g)': '{:.2f}',
                    'Calories': '{:.0f}'
                }))
            else:
                st.info('No foods found within allocated budget.')

import pandas as pd
from robust_average import robust_average

# Demo data for testing
product_df = pd.DataFrame([
    {"Title": "Gourmia 8qt. Digital Air Fryer with Window", "Price": 97.87, "Link": None},
    {"Title": "Gourmia 8qt. Air Fryer Pro", "Price": 109.99, "Link": None},
    {"Title": "Gourmia 8qt. Air Fryer Deluxe", "Price": 129.99, "Link": None},
    {"Title": "Gourmia 8qt. Air Fryer Basic", "Price": 89.99, "Link": None},
    {"Title": "Gourmia 8qt. Air Fryer XL", "Price": 119.99, "Link": None},
])

#step 2.1: Analyze the data (Average price, Median price, Min price, Max price)

# Use robust_average function
robust_result = robust_average(product_df["Price"])
print(f"Robust average: {robust_result['value']} (method: {robust_result['method']})")
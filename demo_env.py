"""
demo_env.py

Demonstrates loading an API key from a .env file using python-dotenv and performing a product search using SerpAPI, Wikidata, and DuckDB.
"""

import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
import duckdb

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
SERAPI_API_KEY = os.getenv("SERPAPI_KEY")

if not SERAPI_API_KEY:
    raise ValueError("API Key not found. Please check your .env file and set API_KEY.")

# --- 1. User Input ---
print("--- Enter Product Details ---")
product_name = input("Enter product name (e.g., iPhone 14 Pro): ")
memory = input("Enter memory/storage (e.g., 256GB): ")
product_number = input("Enter product number: ")
product_condition = input("Enter Product Condition (e.g., New or Used): ")
product_color = input("Enter Product color (e.g., Gold or Blue): ")
location_query = input("Enter search location (e.g., Nigeria): ")
retail_store = input("Enter Retail store (e.g, google): ")
desired_price_count = 10

# --- 2. Build query ---
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

query = """
SELECT ?countryLabel ?isoCode ?tldLabel WHERE {
  ?country wdt:P31 wd:Q6256.                  # Instance of country
  OPTIONAL { ?country wdt:P297 ?isoCode. }           # ISO 3166-1 alpha-2 country code
  OPTIONAL { ?country wdt:P30 ?continent. }         # Continent
  OPTIONAL { 
    ?country wdt:P37 ?language.               # Official language
    OPTIONAL { ?language wdt:P218 ?languageCode. }  # ISO 639-1 language code
  }
  OPTIONAL { ?country wdt:P78 ?tld. }               # Internet TLD

  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en". 
  }
}
ORDER BY ?countryLabel ?languageLabel
"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

data = []
for result in results["results"]["bindings"]:
    country = result.get("countryLabel", {}).get("value", "")
    isoCode = result.get("isoCode", {}).get("value", "")
    tld = result.get("tldLabel", {}).get("value", "")
    data.append({
        "Country": country,
        "ISO Code": isoCode,
        "TLD": tld
    })

domain_df = pd.DataFrame(data)
domain_df = domain_df.drop_duplicates()
engine = retail_store
domain_df["domain"] = domain_df["ISO Code"].apply(lambda x: f"{engine}.{x.lower()}" if x else None)

# --- DuckDB Query ---
country_input = location_query
duckdb.register('df', domain_df)  # Register DataFrame as DuckDB table
# Use LIKE for partial, case-insensitive match
query = f'''
SELECT domain, lower("ISO Code") as "ISO Code"
FROM df
WHERE lower(Country) LIKE '%{country_input.lower()}%'
'''
result_df = duckdb.query(query).to_df()

if result_df.empty:
    raise ValueError(f"No domain info found for country: {country_input}")

search_domain = result_df["domain"].iloc[0]
search_lan = result_df["ISO Code"].iloc[0]

search_string = f"{product_name} {product_number}"
filter_string = f"{product_condition} {product_color} {memory}"

params = {
    "api_key": SERAPI_API_KEY,
    "engine": retail_store,
    "q": search_string,
    "location": location_query,
    "google_domain": search_domain,
    "gl": search_lan,
    "hl": "en",
    "num": "100",
    "uds": filter_string,
    "tbm": "shop"
}

search = requests.get("https://serpapi.com/search", params=params)
response = search.json()

# Debug: Print the full API response
print(json.dumps(response, indent=2))

products = []
for result in response.get("shopping_results", []):
    title = result.get('title')
    price = result.get("extracted_price") or result.get("price")
    link = result.get("link")
    product_data = {
        "Title": title,
        "Price": price,
        "Link": link
    }
    products.append(product_data)

# --- Output Results ---
product_df = pd.DataFrame(products)
print(product_df.head(5)) 
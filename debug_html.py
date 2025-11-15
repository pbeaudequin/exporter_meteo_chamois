#!/usr/bin/env python3
"""
Debug script to see the actual HTML content
"""
import requests
from bs4 import BeautifulSoup

url1 = "https://www.meteo-roquefort-les-pins.com/meteo/currant.html"
url2 = "https://www.meteo-roquefort-les-pins.com/meteo/vantage/valeurs.htm"

print("=" * 80)
print("FETCHING:", url1)
print("=" * 80)

try:
    r1 = requests.get(url1, timeout=10)
    print(f"Status: {r1.status_code}")
    print(f"Content-Type: {r1.headers.get('Content-Type')}")
    print("\n--- RAW HTML (first 2000 chars) ---")
    print(r1.text[:2000])

    soup = BeautifulSoup(r1.text, 'html.parser')
    print("\n--- TEXT CONTENT (first 2000 chars) ---")
    print(soup.get_text()[:2000])

except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("FETCHING:", url2)
print("=" * 80)

try:
    r2 = requests.get(url2, timeout=10)
    print(f"Status: {r2.status_code}")
    print(f"Content-Type: {r2.headers.get('Content-Type')}")
    print("\n--- RAW HTML (first 2000 chars) ---")
    print(r2.text[:2000])

    soup = BeautifulSoup(r2.text, 'html.parser')
    print("\n--- TEXT CONTENT (first 2000 chars) ---")
    print(soup.get_text()[:2000])

    # Look for tables
    tables = soup.find_all('table')
    print(f"\n--- FOUND {len(tables)} TABLES ---")

except Exception as e:
    print(f"ERROR: {e}")

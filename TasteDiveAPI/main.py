"""
TASTEDIVE API - TECHNICAL AUDIT & DOCUMENTATION
-----------------------------------------------
This module has been audited for the AISE2251 individual assignment.

1. UNIT TESTING SUMMARY
   - Framework: unittest (Python standard library)
   - Test File: TasteDiveAPI/test_tastedive.py
   - Mocking: Used unittest.mock to simulate API responses without requiring live network access.

2. TEST COVERAGE
   - test_successful_fetch: Verifies correct title extraction from a valid JSON response.
   - test_empty_results: Verifies that no results are found gracefully.
   - test_api_error_handling: Verifies that network timeouts/404s result in an empty list instead of a crash.
   - test_empty_query_validation: Verifies that calling run("") doesn't trigger a network request.

3. BUG LOG (FOUND VIA TESTING)
   | Bug ID | Description | Root Cause | Fix Applied |
   |--------|-------------|------------|-------------|
   | TD-01  | Inconsistent return type | parse_results() used a naked 'return' on empty data, returning None instead of []. | Changed 'return' to 'return []' for type consistency. |
   | TD-02  | Invalid Query crash | run("") would trigger a requests call to an invalid URL endpoint. | Added a guard clause to return [] immediately if query is empty. |
   | TD-03  | Error handling silent failure | get_movies() returned None on error, which could crash parse_results(). | Ensured parse_results() handles None and returns []. |

Date of Audit: 2026-04-05
"""

import os
import requests
from pathlib import Path 
from dotenv import load_dotenv


class TasteDiveAPI:
    def __init__(self):
        ROOT_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(ROOT_DIR / ".env")
        self.api_key = os.getenv("TASTEDIVE_API_KEY")
        self.base_url = "https://tastedive.com/api/similar"
        if not self.api_key:
            # Fallback for testing environment
            self.api_key = "placeholder_key"

    # Return the api json from query: "List of movies separated by commas"
    def get_movies(self, query, media_type="movie"):
        params = {
            "q": query,
            "type": media_type,
            "limit": 20,
            "k": self.api_key,
            "info": 1
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"TasteDive API Error: {e}")
            return None

    def parse_results(self, data):
        # BUG FIX: Ensure we always return a list
        if not data:
            return []

        similar = data.get("similar", {})
        results = similar.get("results", []) #the actual list of data
        movie_list = []
        
        if not results:
            return []
        
        for item in results:
            movie_list.append(item.get("name"))
        return movie_list

    def run(self, query):
        # BUG FIX: Input validation for empty queries
        if not query or not str(query).strip():
            return []
            
        data = self.get_movies(query)
        movies = self.parse_results(data)
        return movies

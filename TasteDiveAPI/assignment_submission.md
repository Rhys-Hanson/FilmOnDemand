# Assignment Submission: TasteDive API Testing (Task 4)
**Course:** AISE 2251
**Name:** [USER NAME]
**Module:** TasteDive API Individual Component

---

## 1. Test Suite Plan
The test suite for the TasteDive API was designed to verify the core functionality of retrieving and parsing similar movie recommendations while ensuring robustness against network and input errors. 

The suite was developed using the **pytest** framework and utilizes **Double/Mocking** to isolate the API logic from external network dependencies.

### Planned Test Cases:
1.  **test_successful_fetch**: 
    *   **Goal**: Ensure that a valid JSON response from TasteDive is correctly parsed into a list of movie titles.
    *   **Input**: "Batman" (Mocked JSON with 2 results).
    *   **Expected Result**: A python list: `["The Dark Knight", "Inception"]`.
2.  **test_empty_results**: 
    *   **Goal**: Verify the system's behavior when the API returns no matches for a query.
    *   **Input**: "SomeObscureMovie" (Mocked empty results JSON).
    *   **Expected Result**: An empty list `[]`.
3.  **test_api_error_handling**: 
    *   **Goal**: Ensure the module handles network-level errors (timeouts, 404s, 500s) gracefully without crashing the whole application.
    *   **Input**: Simulate a `requests.exceptions.RequestException`.
    *   **Expected Result**: An empty list `[]` and a logged error message.
4.  **test_invalid_query_validation**: 
    *   **Goal**: Test input validation for edge cases like empty strings.
    *   **Input**: An empty string `""`.
    *   **Expected Result**: Immediate return of `[]` to prevent an unnecessary and invalid API call.

---

## 2. Bug Discovery and Handling

During the execution of the initial test plan, the following bugs were identified and remediated:

### Bug TD-01: Inconsistent Return Type (NoneType Error)
- **Discovery**: The `test_empty_results` case failed because the logic used a naked `return` statement when no results were found, which in Python defaults to returning `None`.
- **Impact**: This caused a potential crash in the higher-level "Film On Demand" engine which expected an iterable list.
- **Handling**: Refactored `parse_results()` to explicitly `return []` if the results list was empty or if the input data was malformed.

### Bug TD-02: Invalid Input Crash
- **Discovery**: The `test_invalid_query_validation` case revealed that calling the `run()` method with an empty string would attempt to construct an invalid API URL, leading to a 400 Bad Request.
- **Impact**: Wasted API quota and potential for unhandled 400-level HTTP exceptions.
- **Handling**: Implemented a guard clause at the start of the `run()` method: `if not query or not str(query).strip(): return []`.

### Bug TD-03: Silent Error Failure
- **Discovery**: The `test_api_error_handling` case showed that if the `requests` call failed, the method returned `None`, but the subsequent `parse_results()` call did not have a robust check for `None`, leading to an `AttributeError`.
- **Impact**: Unclear error reporting and system instability during network fluctuations.
- **Handling**: Updated the `get_movies` method to catch `RequestException` and return a safe `None` signal, and ensured `parse_results` treats `None` as an empty data set, returning `[]`.

---

## 3. Execution and Results
The test suite was executed using the following command:
`python3 -m pytest TasteDiveAPI/test_tastedive.py`

**Result:** 4 Passed, 0 Failed.
All identified bugs were successfully fixed, and the code now maintains 100% test pass rate on the identified edge cases.

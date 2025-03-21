# test_fetch.py
from atomreq import fetch_fpds_data

# Test with file output (original behavior)
result1 = fetch_fpds_data(
    last_mod_date="[2022/01/01, 2022/05/01]",
    agency_code="7504",
    output_json="test_output.json"
)

# Test without file output (Lambda behavior)
result2 = fetch_fpds_data(
    last_mod_date="[2022/01/01, 2022/05/01]",
    agency_code="7504"
)

print(f"Test with files: {'Success' if result1 else 'Failed'}")
print(f"Test without files: {'Success' if result2 else 'Failed'}")
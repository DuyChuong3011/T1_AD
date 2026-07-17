import requests
import json

URL = 'https://nd1lr3vdo1.execute-api.ap-southeast-1.amazonaws.com/prod/predict'

# Test 1 — Bình thường (diff nhỏ)
data1 = {
    "sensors": {
        "LV ActivePower (kW)_diff_1": 0.5,
        "Wind Speed (m/s)_diff_1": 0.1,
        "Theoretical_Power_Curve (KWh)_diff_1": 0.2
    },
    "timestamp": "2026-07-15T10:00:00"
}

data2 = {
    "sensors": {
        "LV ActivePower (kW)_diff_1": 50.0,
        "Wind Speed (m/s)_diff_1": 8.0,
        "Theoretical_Power_Curve (KWh)_diff_1": 45.0
    },
    "timestamp": "2026-07-15T10:00:00"
}
print("=== Test 1 — Bình thường ===")
r1 = requests.post(URL, json=data1)
print(json.dumps(r1.json(), indent=2))

print("\n=== Test 2 — Sự cố ===")
r2 = requests.post(URL, json=data2)
print(json.dumps(r2.json(), indent=2))
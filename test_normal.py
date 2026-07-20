# test_normal.py
import requests, json

URL = 'https://nd1lr3vdo1.execute-api.ap-southeast-1.amazonaws.com/prod/predict'

data = {
    "sensors": {
        "LV ActivePower (kW)_diff_1": 0.01,
        "Wind Speed (m/s)_diff_1": 0.01,
        "Theoretical_Power_Curve (KWh)_diff_1": 0.01
    },
    "timestamp": "2026-07-17T10:00:00"
}

r = requests.post(URL, json=data)
print(json.dumps(r.json(), indent=2))
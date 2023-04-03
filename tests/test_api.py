#!/usr/bin/env python3

import requests

url = "https://gettime.ga"
def test_mainpage():
    r = requests.get(url)
    assert r.status_code == 200
def test_apistatus():
    r = requests.get(f"{url}/API/HEALTH")
    assert r.text ==  "OK"
def test_jsonapi():
    params = {
            "school": "IT-Gymnasiet Södertörn",
            "id": "20el2",
            "day": 0
            }
    r = requests.get(f"{url}/API/JSON",params).json()
    assert r['message'] == "OK"
    assert r['status'] ==  0
def test_foodapi():
    params = {"school": "Surteskolan"}
    r = requests.get(f"{url}/API/FOOD_REDIRECT",params)
    assert r.url == "https://skolmaten.se/surteskolan/"
def test_privatelink():
    params = {"school": "IT-Gymnasiet Södertörn", "id": "20el2"}
    r = requests.get(f"{url}/API/SHAREABLE_URL",params)
    assert r.status_code == 200
    assert r.text != None

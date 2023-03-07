#!/usr/bin/env python3

import unittest
import requests

class Test(unittest.TestCase):
    def test_mainpage(self):
        r = requests.get('http://0.0.0.0:7331/')
        self.assertEqual(r.status_code, 200)
    def test_apistatus(self):
        r = requests.get('http://0.0.0.0:7331/API/HEALTH')
        self.assertEqual(r.text, "OK")
    def test_jsonapi(self):
        params = {
                "school": "IT-Gymnasiet Södertörn",
                "id": "20el2",
                "day": 0
                }
        r = requests.get('http://0.0.0.0:7331/API/JSON',params).json()
        self.assertEqual(r['status'], 0)
        self.assertEqual(r['message'], "OK")
    def test_foodapi(self):
        params = {"school": "Surteskolan"}
        r = requests.get('http://0.0.0.0:7331/API/FOOD_REDIRECT',params)
        self.assertEqual(r.url, "https://skolmaten.se/surteskolan/")
    def test_privatelink(self):
        params = {"school": "IT-Gymnasiet Södertörn", "id": "20el2"}
        r = requests.get('http://0.0.0.0:7331/API/SHAREABLE_URL',params)
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.text)

if __name__ == '__main__':
    unittest.main()

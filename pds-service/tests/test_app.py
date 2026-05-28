import unittest
from pds.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_predict_buggy(self):
        #./pandas/pandas/core/algorithms.py;1458;163;289;26;0;2.96;0.0;10;3;159;14;1
        data_tuple = [1458,163,289,26,0,2.96,0.0,10,3,159,14]
        data_tuple = [float(element) for element in data_tuple]
        response = self.client.post('http://127.0.0.1:5000/predict', json={'data_tuple': data_tuple})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['result'], [1])

    def test_predict_not_buggy(self):
        #./pandas/asv_bench/benchmarks/strftime.py;85;0;30;23;3;2.39;7.67;0;0;3;12;0
        data_tuple = [85,0,30,23,3,2.39,7.67,0,0,3,12]
        data_tuple = [float(element) for element in data_tuple]
        response = self.client.post('http://127.0.0.1:5000/predict', json={'data_tuple': data_tuple})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['result'], [0])

if __name__ == '__main__':
    unittest.main()
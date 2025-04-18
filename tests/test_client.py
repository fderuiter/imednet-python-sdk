import unittest

from imednet_sdk.client import ImednetClient


class TestImednetClient(unittest.TestCase):

    def setUp(self):
        self.client = ImednetClient(
            base_url="https://api.imednet.com", api_key="test_api_key"
        )

    def test_get_request(self):
        response = self.client.get("/endpoint")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_post_request(self):
        data = {"key": "value"}
        response = self.client.post("/endpoint", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json(), dict)

    def test_put_request(self):
        data = {"key": "updated_value"}
        response = self.client.put("/endpoint/1", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_delete_request(self):
        response = self.client.delete("/endpoint/1")
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()

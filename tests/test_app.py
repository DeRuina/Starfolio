import unittest
from fastapi.testclient import TestClient
from app.app import app

class TestApp(unittest.TestCase):

  def setUp(self) -> None:
    self.client = TestClient(app)

  def test_root_endpoint(self) -> None:
    response = self.client.get("/")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), {"name": "Dean"})

if __name__ == "__main__":
    unittest.main()
import unittest
from fastapi import Response
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.app import app


class TestApp(unittest.TestCase):

  def setUp(self) -> None:
    self.client = TestClient(app)
 
  def test_missing_state_cookie(self) -> None:
    response = self.client.get("/authorize")
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json(), {"detail": "State cookie not found"})

  def test_missing_authorization_code(self) -> None:
    state_cookie = {"state": "1234567890abcdef"}
    response = self.client.get("/authorize", cookies=state_cookie, params=state_cookie)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json(), {"detail": "No code received"})

  def test_invalid_state_param(self) -> None:
    state_cookie = {"state": "1234567890abcdef"}
    response = self.client.get("/authorize", cookies={"state": "1234567890"}, params=state_cookie)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json(), {"detail": "Invalid state parameter"})
  
  def test_fail_to_get_access_token(self) -> None:
    state_cookie = {"state": "1234567890abcdef"}
    params = {"code": "61651", **state_cookie}
    response = self.client.get("/authorize", cookies=state_cookie, params=params)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json(), {"detail": "Failed to obtain access token"})

  # got this test idea from ChatGPT
  @patch('app.app.exchange_code_for_token')
  @patch('app.app.get_starred_repositories')
  def test_successful_authorization(self, mock_get_starred_repositories, mock_exchange_code_for_token) -> None:
      mock_exchange_code_for_token.return_value = "fake_access_token"
      mock_get_starred_repositories.return_value = Response(content='{"number_of_starred_repositories": 10}', media_type="application/json")
      response = self.client.get("/authorize", cookies={"state": "some_state"}, params={"state": "some_state", "code": "some_code"})
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json(), {"number_of_starred_repositories": 10})


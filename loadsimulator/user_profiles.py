import requests
from locust import HttpUser, task, between, tag
from helpers import generate_user, generate_payment_payload, test_card

# Generalize configurations
API_ENDPOINTS = {
    "REGISTER_USER": "/account/user",
    "AUTH_USER": "/account/user/auth",
    "PAYMENT_METHODS": "/account/user/payments/methods",
    "DELETE_USER": "/account/user",
    ...
}

# General API configurations
API_HEADERS = {
    "CONTENT_TYPE": "application/json",
    "API_KEY": "X-Api-Key",
    "HOST": "api.dev.platform.cloud",
    "ACCESS_TOKEN": "X-User-AccessToken",
    ...
}

class BasicUser(HttpUser):
    """BasicUser is the base class for all users in the load test."""
    timeout = 350

    def on_start(self):
        self.user_data = generate_user()
        self.register_profile()
        self.authorize_user()
        self.register_user_card()

    def on_stop(self):
        self.delete_user()

    def register_profile(self) -> None:
        response = self.client.post(
            API_ENDPOINTS["REGISTER_USER"], json=self.user_data, headers=self.get_request_headers(init_call=True))
        self.user_data["auth_ref"] = response.json()["auth_ref"]

    def authorize_user(self) -> None:
        response = self.client.post(
            API_ENDPOINTS["AUTH_USER"], json=self.user_data, headers=self.get_request_headers(init_call=True))
        self.access_token = response.json()["access_token"]

    def register_user_card(self) -> None:
        self.client.post(API_ENDPOINTS["PAYMENT_METHODS"],
                         json=self.user_data, headers=self.get_request_headers(init_call=True))
        #... Rest of the stripe functions, similar to your example ...

    def delete_user(self) -> None:
        with self.client.delete(API_ENDPOINTS["DELETE_USER"] + "?force=true", headers=self.get_request_headers(init_call=True), catch_response=True) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(f"{response.status_code} - {response.text}")

    def get_request_headers(self, init_call=False) -> dict:
        headers = {API_HEADERS["CONTENT_TYPE"]: 'application/json'}
        
        if init_call:
            headers.update({
                API_HEADERS["API_KEY"]: self.environment.private_api_key,
                API_HEADERS["HOST"]: 'api-private.dev.platform.cloud',
            })
        else:
            api_key = self.environment.public_api_key if isinstance(
                self, PublicUser) else self.environment.private_api_key
            headers.update({
                API_HEADERS["API_KEY"]: api_key,
            })
        
        if hasattr(self, "access_token"):
            headers[API_HEADERS["ACCESS_TOKEN"]] = self.access_token

        return headers

class PrivateUser(BasicUser):
    """PrivateUser performs tasks for the average user in the Private API."""
    wait_time = between(5, 10)

    @task(3)
    def login_user(self) -> None:
        return super().authorize_user()

    @task(4)
    def query_member_profile(self):
        self.client.get(API_ENDPOINTS['QUERY_PROFILE'], headers=self.get_headers())

    # ... rest of the user tasks ...

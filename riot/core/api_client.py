import requests
from riot.config.config import API_LOL
from requests.exceptions import HTTPError


class APIClient:
    def __init__(self, region=None):
        self.region = region
        self.headers = {
            "User-Agent": "DiscordBot (your-bot-name, v1.0)",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": API_LOL
        }

    def get(self, url: str, params: dict = None):
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            self.handle_http_error(response)
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def handle_http_error(self, response):
        status_code = response.status_code
        error_messages = {
            400: "400 Bad Request: The server could not understand the request due to invalid syntax.",
            401: "401 Unauthorized: The client must authenticate itself to get the requested response.",
            403: "403 Forbidden: The client does not have access rights to the content.",
            404: "404 Data Not Found: The server can not find the requested resource.",
            405: "405 Method Not Allowed: The request method is known by the server but is not supported by the target resource.",
            415: "415 Unsupported Media Type: The media format of the requested data is not supported by the server.",
            429: "429 Rate Limit Exceeded: The user has sent too many requests in a given amount of time.",
            500: "500 Internal Server Error: The server has encountered a situation it doesn't know how to handle.",
            502: "502 Bad Gateway: The server, while acting as a gateway or proxy, received an invalid response from the upstream server.",
            503: "503 Service Unavailable: The server is not ready to handle the request.",
            504: "504 Gateway Timeout: The server is acting as a gateway and cannot get a response in time.",
        }

        try:
            error_details = response.json()
            detailed_message = error_details.get('status', {}).get('message', '')
            if detailed_message:
                print(f"{status_code} Error: {detailed_message}")
            else:
                print(error_messages.get(status_code, f"HTTP error occurred: Status Code {status_code}"))
        except ValueError:
            print(error_messages.get(status_code, f"HTTP error occurred: Status Code {status_code}"))

    def get_url(self, base_url, endpoint):
        if self.region:
            base_url = base_url.replace("{REGION}", self.region)
        return f"{base_url}/{endpoint}"

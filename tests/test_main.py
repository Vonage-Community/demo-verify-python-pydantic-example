import unittest
import requests
from config import settings
from vonage_jwt.jwt import JwtClient
from vonage import Auth, Vonage
from vonage_verify import EmailChannel, VerifyRequest


def without_pydantic(request_payload):

    jwt_client = JwtClient(
        application_id=settings.vonage_application_id,
        private_key=settings.vonage_private_key_path,
    )
    jwt_token = jwt_client.generate_application_jwt()

    payload = {
        "brand": request_payload["brand"],
        "workflow": [
            {
                "channel": "email",
                "to": request_payload["to_email"],
            }
        ],
        "channel_timeout": request_payload["channel_timeout"],
        "code_length": request_payload["code_length"],
    }

    response = requests.post(
        "https://api.nexmo.com/v2/verify",
        headers={
            "Authorization": f"Bearer {jwt_token.decode()}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    return response


def with_pydantic(request_payload):
    client = Vonage(
        Auth(
            application_id=settings.vonage_application_id,
            private_key=settings.vonage_private_key_path,
        )
    )

    verify_request = VerifyRequest(
        brand=request_payload["brand"],
        workflow=[EmailChannel(to=request_payload["to_email"])],
        channel_timeout=request_payload["channel_timeout"],
        code_length=request_payload["code_length"],
    )

    client.verify.start_verification(verify_request)
    last_response = client.http_client.last_response

    return last_response


class TestMain(unittest.TestCase):

    test_data = {
        "brand": 12345,
        "to_email": 678910,
        "channel_timeout": "sixty",
        "code_length": "five",
    }

    def test_without_pydantic(self):

        expected_result = 202
        test_result = without_pydantic(self.test_data)

        self.assertEqual(
            test_result.status_code,
            expected_result,
            msg=f"Test without Pydantic failed with: {test_result.status_code}. Expected: {expected_result}",
        )

    def test_with_pydantic(self):

        expected_result = 202
        test_result = with_pydantic(self.test_data)

        self.assertEqual(
            test_result.status_code,
            expected_result,
            msg=f"Test with Pydantic failed with: {test_result.status_code}. Expected: {expected_result}",
        )
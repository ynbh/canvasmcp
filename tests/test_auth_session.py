import pytest
import requests

from auth.session import apply_chrome_session_to_http_session


@pytest.mark.parametrize(
    ("cookie_token", "header_token"),
    [
        ("token%2Bvalue%2Fpart%3D%3D", "token+value/part=="),
        ("token+value/part==", "token+value/part=="),
    ],
)
def test_csrf_header_is_decoded_and_cookie_is_preserved(cookie_token, header_token):
    with requests.Session() as session:
        apply_chrome_session_to_http_session(
            session,
            base_url="https://school.instructure.com",
            cookies=("session-value", cookie_token),
        )
        request = session.prepare_request(
            requests.Request("POST", "https://school.instructure.com/api/v1/files")
        )

    assert request.headers["X-CSRF-Token"] == header_token
    assert f"_csrf_token={cookie_token}" in request.headers["Cookie"]
    assert "canvas_session=session-value" in request.headers["Cookie"]

"""Example REST API validation test — adapt the base URL, endpoints, and assertions.

Uses the public JSONPlaceholder API (https://jsonplaceholder.typicode.com) so the
test runs without any configuration changes.  Replace the base URL and endpoint
paths once you point it at your own service.

Run:
    pytest tests/demo/functional/api/test_demo_api.py
"""
import pytest
from utils.api_client import ApiClient
from utils.response_validator import ResponseValidator
from utils.logger import get_logger

logger = get_logger("test_demo_api")

BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="module")
def api_client():
    """Shared API client for this module.

    Note: verify_ssl=False disables SSL certificate verification.
    This is useful in corporate environments with proxies/firewalls.
    Set verify_ssl=True in production for security.
    """
    return ApiClient(
        base_url=BASE_URL,
        timeout_seconds=10,
        retries=2,
        logger=logger,
        verify_ssl=False,  # Disable for testing - enable in production
    )


@pytest.mark.smoke
@pytest.mark.api
def test_get_posts_returns_list(api_client):
    """GET /posts must return HTTP 200 with a non-empty JSON array."""
    response = api_client.get("/posts")

    ResponseValidator.assert_status_code(response, 200)
    ResponseValidator.assert_response_time_less_than(response, 2000)

    posts = response.json()
    assert isinstance(posts, list), "Expected a JSON array"
    assert len(posts) > 0, "Posts list must not be empty"
    logger.info(f"GET /posts returned {len(posts)} items")


@pytest.mark.smoke
@pytest.mark.api
def test_get_single_post_schema(api_client):
    """GET /posts/1 must return a document with the expected fields."""
    response = api_client.get("/posts/1")

    ResponseValidator.assert_status_code(response, 200)
    ResponseValidator.assert_json_has_keys(response, ["userId", "id", "title", "body"])
    ResponseValidator.assert_json_value(response, "id", 1)
    logger.info("POST schema validation passed")


@pytest.mark.regression
@pytest.mark.api
def test_create_post_returns_201(api_client):
    """POST /posts must create a resource and echo back the payload."""
    payload = {"title": "QE smoke test", "body": "automated", "userId": 1}
    response = api_client.post("/posts", json_body=payload)

    ResponseValidator.assert_status_code(response, 201)
    ResponseValidator.assert_response_time_less_than(response, 2000)

    created = response.json()
    assert created["title"] == payload["title"], "Title not echoed back"
    assert "id" in created, "New resource must have an id"
    logger.info(f"Created post with id={created['id']}")


@pytest.mark.negative
@pytest.mark.api
def test_get_nonexistent_resource_returns_404(api_client):
    """GET on a non-existent resource must return HTTP 404."""
    response = api_client.get("/posts/999999")
    ResponseValidator.assert_status_code(response, 404)
    logger.info("404 handled correctly for unknown resource")

# API Tests

## Purpose
API tests validate REST API endpoints, request/response handling, and business logic.

## Organization
Tests are organized by **domain** or **resource**:
- `authentication/` - Login, logout, token management
- `users/` - User CRUD operations
- `orders/` - Order management APIs

## Naming Convention
- `test_<resource>_<operation>.py`
- Example: `test_user_creation.py`, `test_order_status.py`

## Example Structure
```python
# tests/functional/api/users/test_user_creation.py
import pytest
from utils.api_client import ApiClient
from utils.response_validator import ResponseValidator

@pytest.mark.smoke
@pytest.mark.api
def test_create_user_returns_201(api_client):
    payload = {"name": "Test User", "email": "test@example.com"}
    response = api_client.post("/users", json_body=payload)

    ResponseValidator.assert_status_code(response, 201)
    ResponseValidator.assert_json_has_keys(response, ["id", "name", "email"])
```

## Running API Tests
```bash
# Run all API tests
pytest tests/functional/api/

# Run specific domain
pytest tests/functional/api/users/

# Run with specific environment
pytest tests/functional/api/ --pyplaykit-env qa
```

## Best Practices
1. Use `ApiClient` from `utils/api_client.py` for all HTTP requests
2. Use `ResponseValidator` for assertions
3. Test both success and error scenarios
4. Use appropriate markers and tags
5. Keep test data in `test_data/` directory

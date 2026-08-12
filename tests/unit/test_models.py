import pytest
from pydantic import ValidationError
from src.models.user import CreateUserRequest, ErrorResponse

def test_create_user_request_accepts_valid_data():
    req = CreateUserRequest(name="Jane Doe", email="jane@example.com", age=30)
    assert req.age == 30

@pytest.mark.parametrize("age", [0, 151, -1])
def test_create_user_request_rejects_out_of_range_age(age):
    with pytest.raises(ValidationError):
        CreateUserRequest(name="Jane Doe", email="jane@example.com", age=age)

def test_create_user_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        CreateUserRequest(name="Jane Doe", email="not-an-email", age=30)

def test_error_response_requires_error_field():
    with pytest.raises(ValidationError):
        ErrorResponse()

import pytest
from pydantic import ValidationError
from src.models.user import User, CreateUserRequest, UpdateUserRequest, ErrorResponse

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

def test_user_accepts_valid_data():
    user = User(name="John Doe", email="john@example.com", age=25)
    assert user.age == 25
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_update_user_request_accepts_valid_data():
    req = UpdateUserRequest(name="Jane Smith", email="jane.smith@example.com", age=28)
    assert req.age == 28
    assert req.name == "Jane Smith"
    assert req.email == "jane.smith@example.com"

@pytest.mark.parametrize("age", [1, 150])
def test_create_user_request_accepts_boundary_ages(age):
    req = CreateUserRequest(name="Jane Doe", email="jane@example.com", age=age)
    assert req.age == age

@pytest.mark.parametrize("age", [1, 150])
def test_user_accepts_boundary_ages(age):
    user = User(name="Jane Doe", email="jane@example.com", age=age)
    assert user.age == age

@pytest.mark.parametrize("age", [1, 150])
def test_update_user_request_accepts_boundary_ages(age):
    req = UpdateUserRequest(name="Jane Doe", email="jane@example.com", age=age)
    assert req.age == age

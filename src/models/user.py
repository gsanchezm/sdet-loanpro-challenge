from pydantic import BaseModel, EmailStr, Field

class UserPayload(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=1, le=150)

class User(UserPayload):
    pass

class CreateUserRequest(UserPayload):
    pass

class UpdateUserRequest(UserPayload):
    pass

class ErrorResponse(BaseModel):
    error: str

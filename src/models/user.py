from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=1, le=150)

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=1, le=150)

class UpdateUserRequest(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=1, le=150)

class ErrorResponse(BaseModel):
    error: str

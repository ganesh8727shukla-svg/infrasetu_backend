from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    userId: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = Field(pattern="^(admin|citizen|contractor)$")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    role: str
    organisation: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    user: UserOut

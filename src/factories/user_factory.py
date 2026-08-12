import uuid
from faker import Faker

_faker = Faker()
TEST_EMAIL_DOMAIN = "sdet-test.dev"


class UserFactory:
    @staticmethod
    def valid_payload(**overrides) -> dict:
        payload = {
            "name": _faker.name(),
            "email": f"qa-{uuid.uuid4()}@{TEST_EMAIL_DOMAIN}",
            "age": _faker.random_int(min=1, max=150),
        }
        payload.update(overrides)
        return payload


class UserPayloadBuilder:
    def __init__(self):
        self._payload = UserFactory.valid_payload()

    def with_name(self, value) -> "UserPayloadBuilder":
        self._payload["name"] = value
        return self

    def with_email(self, value) -> "UserPayloadBuilder":
        self._payload["email"] = value
        return self

    def with_age(self, value) -> "UserPayloadBuilder":
        self._payload["age"] = value
        return self

    def without_field(self, field_name: str) -> "UserPayloadBuilder":
        self._payload.pop(field_name, None)
        return self

    def with_extra_field(self, key: str, value) -> "UserPayloadBuilder":
        self._payload[key] = value
        return self

    def build(self) -> dict:
        return dict(self._payload)

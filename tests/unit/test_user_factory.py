from src.factories.user_factory import UserFactory, UserPayloadBuilder


def test_valid_payload_has_qa_prefixed_email():
    payload = UserFactory.valid_payload()
    assert payload["email"].startswith("qa-")
    assert 1 <= payload["age"] <= 150


def test_valid_payload_supports_overrides():
    payload = UserFactory.valid_payload(age=45)
    assert payload["age"] == 45


def test_builder_can_omit_a_required_field():
    payload = UserPayloadBuilder().without_field("email").build()
    assert "email" not in payload


def test_builder_can_set_out_of_range_age():
    payload = UserPayloadBuilder().with_age(151).build()
    assert payload["age"] == 151


def test_builder_can_add_unexpected_field():
    payload = UserPayloadBuilder().with_extra_field("role", "admin").build()
    assert payload["role"] == "admin"

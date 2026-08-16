"""Validating inputs using regular expressions."""

import re

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
PHONE_PATTERN = re.compile(r"^\+?[\d\s\-()]{10,20}$")
PROPERTY_ID_PATTERN = re.compile(r"^PROP-\d{4}$")
TENANT_ID_PATTERN = re.compile(r"^TEN-\d{4}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.match(phone.strip()))


def validate_property_id(property_id: str) -> bool:
    return bool(PROPERTY_ID_PATTERN.match(property_id.strip().upper()))


def validate_tenant_id(tenant_id: str) -> bool:
    return bool(TENANT_ID_PATTERN.match(tenant_id.strip().upper()))

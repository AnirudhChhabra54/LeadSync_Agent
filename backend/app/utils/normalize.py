"""
Phone and email normalization utilities for deduplication.
"""

import re


def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number by stripping all non-digit characters and standardizing.
    Strips leading zeros and common country code prefixes so that e.g. +91 98765 43210,
    91-9876543210, and 9876543210 match.
    """
    if not phone:
        return ""

    # Remove all non-digit characters
    digits = re.sub(r"\D", "", str(phone))
    digits = digits.lstrip("0")

    # If phone has 10 or more digits, standardizing to last 10 digits provides robust matching across country codes
    if len(digits) >= 10:
        return digits[-10:]

    return digits


def normalize_email(email: str) -> str:
    """
    Normalize an email address: lowercase, strip whitespace.
    """
    if not email:
        return ""
    return str(email).strip().lower()

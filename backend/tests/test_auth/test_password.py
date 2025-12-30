"""Tests for password hashing and verification."""

import pytest
from jobly.auth.password import hash_password, verify_password


def test_password_hashing():
    """Test password hashing."""
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)


def test_password_verification_success():
    """Test successful password verification."""
    password = "MySecretPassword"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_password_verification_failure():
    """Test failed password verification."""
    password = "CorrectPassword"
    wrong_password = "WrongPassword"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_different_hashes_for_same_password():
    """Test that same password produces different hashes (due to salt)."""
    password = "SamePassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2
    # But both should verify successfully
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_empty_password():
    """Test handling of empty password."""
    password = ""
    hashed = hash_password(password)

    assert verify_password("", hashed) is True
    assert verify_password("notempty", hashed) is False

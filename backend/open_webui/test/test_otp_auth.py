import smtplib
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from open_webui.routers.auths import (
    _normalize_otp_email,
    _otp_hash,
    _send_otp_email,
)


def test_otp_hash_is_stable_and_not_plaintext():
    first = _otp_hash('student@students.example.edu', '012345')
    assert first == _otp_hash('student@students.example.edu', '012345')
    assert first != '012345'
    assert len(first) == 64


def test_non_university_email_is_rejected(monkeypatch):
    monkeypatch.setattr('open_webui.routers.auths.OTP_ALLOWED_EMAIL_DOMAINS', ('students.example.edu',))
    with pytest.raises(HTTPException) as error:
        _normalize_otp_email('student@not-approved.example')
    assert error.value.status_code in {400, 403}


def test_otp_email_uses_configured_smtp(monkeypatch):
    for name, value in {
        'OTP_SMTP_HOST': 'smtp.example.edu',
        'OTP_SMTP_PORT': 587,
        'OTP_SMTP_USERNAME': 'sender@example.edu',
        'OTP_SMTP_PASSWORD': 'app-password',
        'OTP_EMAIL_FROM': 'sender@example.edu',
        'OTP_SMTP_USE_TLS': True,
    }.items():
        monkeypatch.setattr(f'open_webui.routers.auths.{name}', value)
    smtp = MagicMock(spec=smtplib.SMTP)
    with patch('open_webui.routers.auths.smtplib.SMTP', return_value=smtp):
        _send_otp_email('student@students.example.edu', '012345')
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once()
    smtp.sendmail.assert_called_once()

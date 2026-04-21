#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from unittest import mock

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test import override_settings

from django_altcha import AltchaField

from .test_field import make_valid_payload


class AltchaFieldLoggingTest(TestCase):
    def setUp(self):
        class TestForm(forms.Form):
            altcha_field = AltchaField()

        self.form_class = TestForm

    @mock.patch("altcha.verify_solution_v1")
    def test_invalid_token_logs_warning(self, mock_verify_solution):
        mock_verify_solution.return_value = (False, "bad signature")
        form = self.form_class(data={"altcha_field": "anything"})
        with self.assertLogs("django_altcha", level="WARNING") as captured:
            form.is_valid()
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].levelname, "WARNING")
        self.assertIn("bad signature", captured.output[0])

    @mock.patch("altcha.verify_solution_v1")
    def test_verification_exception_is_logged_with_traceback(
        self, mock_verify_solution
    ):
        mock_verify_solution.side_effect = RuntimeError("boom")
        form = self.form_class(data={"altcha_field": "anything"})
        with self.assertLogs("django_altcha", level="ERROR") as captured:
            form.is_valid()
        self.assertEqual(captured.records[0].levelname, "ERROR")
        # Confirms traceback is captured
        self.assertIsNotNone(captured.records[0].exc_info)

    @mock.patch("altcha.verify_solution_v1")
    def test_replay_attempt_logs_warning(self, mock_verify_solution):
        mock_verify_solution.return_value = (True, None)
        valid_payload = make_valid_payload(challenge="replay-test-1")
        # First submission succeeds and marks the challenge as used.
        self.form_class(data={"altcha_field": valid_payload}).is_valid()
        # Second submission should log a replay warning.
        form = self.form_class(data={"altcha_field": valid_payload})
        with self.assertLogs("django_altcha", level="WARNING") as captured:
            form.is_valid()
        self.assertTrue(
            any("replay" in r.getMessage().lower() for r in captured.records)
        )

    @override_settings(ALTCHA_HMAC_KEY=None)
    def test_missing_hmac_key_logs_error(self):
        from django_altcha import get_hmac_key

        with self.assertLogs("django_altcha", level="ERROR") as captured:
            with self.assertRaises(ImproperlyConfigured):
                get_hmac_key()
        self.assertEqual(captured.records[0].levelname, "ERROR")

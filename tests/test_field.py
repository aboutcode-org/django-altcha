#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from unittest import mock

from django import forms
from django.test import TestCase

from django_altcha import ALTCHA_CHALLENGE_EXPIRE
from django_altcha import AltchaField
from django_altcha import AltchaWidget


class DjangoAltchaFieldTest(TestCase):
    def setUp(self):
        class TestForm(forms.Form):
            altcha_field = AltchaField()

        self.form_class = TestForm

    def test_altcha_field_renders_widget(self):
        form = self.form_class()
        self.assertIsInstance(form.fields["altcha_field"].widget, AltchaWidget)

    def test_altcha_field_widget_default_options(self):
        altcha_field = AltchaField()
        self.assertEqual(ALTCHA_CHALLENGE_EXPIRE, altcha_field.widget.options["expire"])
        altcha_field = AltchaField(expire=1)
        self.assertEqual(1, altcha_field.widget.options["expire"])
        altcha_field = AltchaField(expire=None)
        self.assertEqual(None, altcha_field.widget.options["expire"])

    def test_altcha_field_options_to_widget(self):
        altcha_field = AltchaField(maxnumber=50, expire=10000)
        self.assertEqual(50, altcha_field.widget.options["maxnumber"])
        self.assertEqual(10000, altcha_field.widget.options["expire"])

    def test_altcha_field_with_missing_value_raises_required_error(self):
        form = self.form_class(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("altcha_field", form.errors)
        self.assertEqual(
            form.errors["altcha_field"][0], "ALTCHA CAPTCHA token is missing."
        )

    @mock.patch("altcha.verify_solution")
    def test_altcha_field_validation_calls_verify_solution(self, mock_verify_solution):
        mock_verify_solution.return_value = (True, None)
        form = self.form_class(data={"altcha_field": "valid_token"})
        self.assertTrue(form.is_valid())
        mock_verify_solution.assert_called_once_with(
            payload="valid_token",
            hmac_key=mock.ANY,
            check_expires=True,
        )

    @mock.patch("altcha.verify_solution")
    def test_altcha_field_validation_fails_on_invalid_token(self, mock_verify_solution):
        mock_verify_solution.return_value = (False, "Invalid token")
        form = self.form_class(data={"altcha_field": "invalid_token"})
        self.assertFalse(form.is_valid())
        self.assertIn("altcha_field", form.errors)
        self.assertEqual(form.errors["altcha_field"][0], "Invalid CAPTCHA token.")

    @mock.patch("altcha.verify_solution")
    def test_altcha_field_validation_handles_exception(self, mock_verify_solution):
        mock_verify_solution.side_effect = Exception("Verification failed")
        form = self.form_class(data={"altcha_field": "some_token"})
        self.assertFalse(form.is_valid())
        self.assertIn("altcha_field", form.errors)
        self.assertEqual(
            form.errors["altcha_field"][0], "Failed to process CAPTCHA token"
        )

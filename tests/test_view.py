#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from django.test import TestCase
from django.urls import reverse


class DjangoAltchaViewTest(TestCase):
    def test_challenge_view_returns_200(self):
        response = self.client.get(reverse("altcha_challenge"))
        self.assertEqual(response.status_code, 200)

    def test_challenge_view_returns_json(self):
        response = self.client.get(reverse("altcha_challenge"))
        self.assertEqual(response["Content-Type"], "application/json")

    def test_challenge_response_contains_expected_keys(self):
        response = self.client.get(reverse("altcha_challenge"))
        data = response.json()

        expected_keys = ["algorithm", "challenge", "max_number", "salt", "signature"]
        self.assertEqual(expected_keys, list(data.keys()))

        self.assertEqual("SHA-256", data["algorithm"])
        self.assertEqual(100, data["max_number"])

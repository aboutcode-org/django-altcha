#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from django.test import TestCase

from django_altcha import get_altcha_challenge


class DjangoAltchaUtilsTest(TestCase):
    def test_get_altcha_challenge_max_number(self):
        challenge = get_altcha_challenge()
        self.assertEqual(1000000, challenge.maxnumber)
        challenge = get_altcha_challenge(max_number=50)
        self.assertEqual(50, challenge.maxnumber)

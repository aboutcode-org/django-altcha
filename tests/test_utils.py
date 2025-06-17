#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from datetime import datetime
from unittest import mock

from django.test import TestCase

from django_altcha import get_altcha_challenge

mock_now = datetime(2025, 10, 10)


class DjangoAltchaUtilsTest(TestCase):
    def test_get_altcha_challenge_max_number(self):
        challenge = get_altcha_challenge()
        self.assertEqual(1000000, challenge.max_number)
        challenge = get_altcha_challenge(max_number=50)
        self.assertEqual(50, challenge.max_number)

    @mock.patch("django_altcha.datetime.datetime")
    def test_get_altcha_challenge_expire(self, mock_datetime):
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Default ALTCHA_CHALLENGE_EXPIRE is applied
        challenge = get_altcha_challenge()
        salt_expires = challenge.salt.split("?expires=")[-1]
        self.assertEqual("1760073600", salt_expires)

        # Provided `expires` argument is applied
        challenge = get_altcha_challenge(expires=10000)
        salt_expires = challenge.salt.split("?expires=")[-1]
        self.assertEqual("1760072410", salt_expires)

        # Custom ALTCHA_CHALLENGE_EXPIRE value is applied
        with mock.patch("django_altcha.ALTCHA_CHALLENGE_EXPIRE", 9999):
            challenge = get_altcha_challenge()
            salt_expires = challenge.salt.split("?expires=")[-1]
            self.assertEqual("1760072409", salt_expires)

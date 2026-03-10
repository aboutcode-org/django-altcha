#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import time
import unittest
from unittest import mock

from django.core.cache.backends.locmem import LocMemCache
from django.test import override_settings

from django_altcha import get_cache
from django_altcha import get_challenge_expire_seconds
from django_altcha import is_challenge_used
from django_altcha import mark_challenge_used
from django_altcha.conf import get_setting


class DjangoAltchaCacheTest(unittest.TestCase):
    def setUp(self):
        self.challenge = "test-challenge-123"

    @override_settings(ALTCHA_CACHE_ALIAS="altcha")
    @mock.patch("django_altcha.caches")
    def test_get_cache_with_alias(self, mock_caches):
        get_cache()
        mock_caches.__getitem__.assert_called_once_with("altcha")

    def test_get_cache_without_alias_uses_default(self):
        self.assertEqual("default", get_setting("ALTCHA_CACHE_ALIAS"))
        cache = get_cache()
        self.assertIsInstance(cache, LocMemCache)

    def test_mark_and_check_challenge_used(self):
        cache = get_cache()
        cache.clear()

        self.assertFalse(is_challenge_used(self.challenge))
        mark_challenge_used(self.challenge, timeout=get_challenge_expire_seconds())
        self.assertTrue(is_challenge_used(self.challenge))

    def test_challenge_expires(self):
        cache = get_cache()
        cache.clear()

        mark_challenge_used(self.challenge, timeout=1)  # 1 second timeout
        self.assertTrue(is_challenge_used(self.challenge))
        time.sleep(1.1)
        self.assertFalse(is_challenge_used(self.challenge))

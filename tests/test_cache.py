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

from django_altcha import ALTCHA_CHALLENGE_EXPIRE_SECONDS
from django_altcha import get_altcha_cache
from django_altcha import is_challenge_used
from django_altcha import mark_challenge_used


class DjangoAltchaCacheTest(unittest.TestCase):
    def setUp(self):
        self.challenge = "test-challenge-123"

    @override_settings(ALTCHA_CACHE_ALIAS="altcha")
    @mock.patch("django_altcha.caches")
    def test_get_altcha_cache_with_alias(self, mock_caches):
        get_altcha_cache()
        mock_caches.__getitem__.assert_called_once_with("altcha")

    @override_settings(ALTCHA_CACHE_ALIAS=None)
    def test_get_altcha_cache_without_alias_uses_locmemcache(self):
        cache = get_altcha_cache()
        self.assertIsInstance(cache, LocMemCache)
        self.assertEqual(cache.default_timeout, ALTCHA_CHALLENGE_EXPIRE_SECONDS)

    def test_mark_and_check_challenge_used(self):
        cache = get_altcha_cache()
        cache.clear()

        self.assertFalse(is_challenge_used(self.challenge))
        mark_challenge_used(self.challenge, timeout=ALTCHA_CHALLENGE_EXPIRE_SECONDS)
        self.assertTrue(is_challenge_used(self.challenge))

    def test_challenge_expires(self):
        cache = get_altcha_cache()
        cache.clear()

        mark_challenge_used(self.challenge, timeout=1)  # 1 second timeout
        self.assertTrue(is_challenge_used(self.challenge))
        time.sleep(1.1)
        self.assertFalse(is_challenge_used(self.challenge))

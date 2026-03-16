#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

"""
Lazy settings access for django-altcha.

Django settings read at module import time can capture stale or default
values if the module is imported before settings are fully configured.
This module avoids that by deferring all reads to call time through
django.conf.settings, which is a lazy object guaranteed to reflect the
final project configuration.
"""

from django.conf import settings

from django_altcha.utils import lazy_static

_DEFAULTS = {
    # Set to `False` to skip Altcha validation altogether.
    "ALTCHA_VERIFICATION_ENABLED": True,
    # This key is used to HMAC-sign ALTCHA challenges and must be kept secret.
    "ALTCHA_HMAC_KEY": None,
    # URL of the Altcha JavaScript file.
    # Defaults to the bundled django-altcha file.
    "ALTCHA_JS_URL": lazy_static("altcha/altcha.min.js"),
    # URL of the Altcha translations JavaScript file.
    # Defaults to the bundled django-altcha file.
    "ALTCHA_JS_TRANSLATIONS_URL": lazy_static("altcha/dist_i18n/all.min.js"),
    # Whether to include Altcha translations.
    # https://altcha.org/docs/v2/widget-integration/#internationalization-i18n
    "ALTCHA_INCLUDE_TRANSLATIONS": False,
    # Challenge expiration duration in milliseconds.
    # Default to 20 minutes as per Altcha security recommendations.
    # https://altcha.org/docs/v2/security-recommendations/
    "ALTCHA_CHALLENGE_EXPIRE": 1200000,
    # Django cache alias used to store challenge data for replay attack protection.
    # Defaults to the "default" cache backend.
    # https://docs.djangoproject.com/en/dev/ref/settings/#caches
    "ALTCHA_CACHE_ALIAS": "default",
}


def get_setting(name):
    """Look up a django-altcha setting, falling back to the default."""
    if name not in _DEFAULTS:
        raise ValueError(f"Unknown django-altcha setting: {name}")
    return getattr(settings, name, _DEFAULTS[name])

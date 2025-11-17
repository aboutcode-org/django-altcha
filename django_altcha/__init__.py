#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import base64
import datetime
import json
import secrets
import warnings

from django import forms
from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.locmem import LocMemCache
from django.forms.widgets import HiddenInput
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_GET

import altcha

__version__ = "0.4.0"
VERSION = __version__

# Set to `False` to skip Altcha validation altogether.
ALTCHA_VERIFICATION_ENABLED = getattr(settings, "ALTCHA_VERIFICATION_ENABLED", True)

ALTCHA_HMAC_KEY = getattr(settings, "ALTCHA_HMAC_KEY", None)
if not ALTCHA_HMAC_KEY:
    warnings.warn(
        (
            "ALTCHA_HMAC_KEY is not set in settings. "
            "A random key is being generated, which is insecure and "
            "may lead to signature mismatches in multi-worker deployments. "
            "This fallback behavior will be removed in a future release. "
            "Set ALTCHA_HMAC_KEY in your Django settings."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    ALTCHA_HMAC_KEY = secrets.token_hex(32)

ALTCHA_JS_URL = getattr(settings, "ALTCHA_JS_URL", "/static/altcha/altcha.min.js")
ALTCHA_INCLUDE_TRANSLATIONS = getattr(settings, "ALTCHA_INCLUDE_TRANSLATIONS", False)
ALTCHA_JS_TRANSLATIONS = "/static/altcha/dist_i18n/all.min.js"

# Challenge expiration duration in milliseconds.
# Default to 20 minutes as per Altcha security recommendations.
# https://altcha.org/docs/v2/security-recommendations/
ALTCHA_CHALLENGE_EXPIRE = getattr(settings, "ALTCHA_CHALLENGE_EXPIRE", 1200000)
ALTCHA_CHALLENGE_EXPIRE_SECONDS = ALTCHA_CHALLENGE_EXPIRE // 1000


def get_altcha_cache():
    """
    Returns a Django cache backend instance to be used for storing ALTCHA challenge
    data, especially for replay attack protection.

    - If the setting `ALTCHA_CACHE_ALIAS` is set, the cache with that alias
      will be used.
    - If not set, a local in-memory cache will be used with a timeout matching
      the challenge expiration in seconds.
    """
    cache_alias = getattr(settings, "ALTCHA_CACHE_ALIAS", None)
    if cache_alias:
        return caches[cache_alias]

    # Use the same timeout for the cache as the challenge expiration to ensure
    # cached challenges expire in sync with their validity period.
    params = {"timeout": ALTCHA_CHALLENGE_EXPIRE_SECONDS}
    return LocMemCache(name="altcha_local", params=params)


_altcha_cache = get_altcha_cache()


def is_challenge_used(challenge):
    """Check if a challenge has already been used."""
    return _altcha_cache.get(key=challenge) is not None


def mark_challenge_used(challenge, timeout):
    """Mark a challenge as used by storing it in the cache with a timeout."""
    _altcha_cache.set(key=challenge, value=True, timeout=timeout)


def get_altcha_challenge(max_number=None, expires=None):
    """
    Generate and return an ALTCHA challenge.

    Attributes:
        max_number (int): Maximum number to use for the challenge.
        expires (int): Expiration time for the challenge in milliseconds.

    Returns:
        altcha.Challenge: The generated challenge.
    """
    expires = expires or ALTCHA_CHALLENGE_EXPIRE
    options = {
        "hmac_key": ALTCHA_HMAC_KEY,
        "expires": datetime.datetime.now() + datetime.timedelta(milliseconds=expires),
    }

    if max_number is not None:
        options["max_number"] = max_number

    challenge = altcha.create_challenge(altcha.ChallengeOptions(**options))
    return challenge


class AltchaWidget(HiddenInput):
    template_name = "altcha_widget.html"

    def __init__(self, options, *args, **kwargs):
        """Initialize the ALTCHA widget with provided options from the field."""
        self.options = options or {}
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        """Generate the widget context, including ALTCHA JS URL and challenge."""
        context = super().get_context(name, value, attrs)
        context["js_src_url"] = ALTCHA_JS_URL
        context["include_trans"] = ALTCHA_INCLUDE_TRANSLATIONS
        context["js_trans"] = ALTCHA_JS_TRANSLATIONS

        # If a `challengeurl` is provided, the challenge will be fetched from this URL.
        # This can be a local Django view or an external API endpoint.
        # If not provided, a unique challenge is generated locally in a self-hosted
        # mode.
        # Since the challenge must be fresh for each form rendering, it is generated
        # inside `get_context`, not `__init__`.
        if not self.options.get("challengeurl"):
            challenge = get_altcha_challenge(
                max_number=self.options.get("maxnumber"),
                expires=self.options.get("expire"),
            )
            self.options["challengejson"] = json.dumps(challenge.__dict__)

        # JSON-encode list/dict values before setting in context
        encoded_options = self.encode_values(self.options)
        context["widget"]["altcha_options"] = encoded_options

        return context

    @staticmethod
    def encode_values(data):
        """Return a shallow copy of `data` where lists and dicts are JSON encoded."""
        encoded = {}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            encoded[key] = value
        return encoded


class AltchaField(forms.Field):
    widget = AltchaWidget
    default_error_messages = {
        "error": _("Failed to process CAPTCHA token"),
        "invalid": _("Invalid CAPTCHA token."),
        "required": _("ALTCHA CAPTCHA token is missing."),
        "replay": _("Challenge has already been used."),
    }
    default_options = {
        ## Required options:
        #
        # URL of your server to fetch the challenge from.
        "challengeurl": None,
        # JSON-encoded challenge data.
        # If avoiding an HTTP request to challengeurl, provide the data here.
        "challengejson": None,
        ## Additional options:
        #
        # Automatically verify without user interaction.
        # Possible values: "off", "onfocus", "onload", "onsubmit".
        "auto": None,
        # Whether to include credentials with the challenge request
        # Possible values: "omit", "same-origin", "include".
        "credentials": None,
        # A custom fetch function for retrieving the challenge.
        # Accepts `url: string` and `init: RequestInit` as arguments and must return a
        # `Response`.
        "customfetch": None,
        # Artificial delay before verification (in milliseconds, default: 0).
        "delay": None,
        # If true, prevents the code-challenge input from automatically receiving
        # focus on render (defaults to "false").
        "disableautofocus": None,
        # Challenge expiration duration (in milliseconds).
        "expire": ALTCHA_CHALLENGE_EXPIRE,
        # Enable floating UI.
        # Possible values: "auto", "top", "bottom".
        "floating": None,
        # CSS selector of the “anchor” to which the floating UI is attached.
        # Default: submit button in the related form.
        "floatinganchor": None,
        # Y offset from the anchor element for the floating UI (in pixels, default: 12).
        "floatingoffset": None,
        # Enable a “persistent” mode to keep the widget visible under specific
        # conditions.
        # Possible values: "true", "false", "focus".
        "floatingpersist": None,
        # Hide the footer (ALTCHA link).
        "hidefooter": None,
        # Hide the ALTCHA logo.
        "hidelogo": None,
        # The checkbox id attribute.
        # Useful for multiple instances of the widget on the same page.
        "id": None,
        # The ISO alpha-2 code of the language to use
        # (the language file be imported from `altcha/i18n/*`).
        "language": None,
        # Max number to iterate to (default: 1,000,000).
        "maxnumber": None,
        # Name of the hidden field containing the payload (defaults to "altcha").
        "name": None,
        # Enables overlay UI mode (automatically sets `auto="onsubmit"`).
        "overlay": None,
        # CSS selector of the HTML element to display in the overlay modal before the
        # widget.
        "overlaycontent": None,
        # JSON-encoded translation strings for customization.
        "strings": None,
        # Automatically re-fetch and re-validate when the challenge expires
        # (default: true).
        "refetchonexpire": None,
        # Number of workers for Proof of Work (PoW).
        # Default: navigator.hardwareConcurrency or 8 (max value: 16).
        "workers": None,
        # URL of the Worker script (default: ./worker.js, only for external builds).
        "workerurl": None,
        # Data Obfuscation options:
        #
        # The obfuscated data provided as a base64-encoded string (requires
        # altcha/obfuscation plugin).
        # Use only without challengeurl/challengejson.
        "obfuscated": None,
        ## Development / testing options:
        #
        # Print log messages in the console (for debugging).
        "debug": None,
        # Causes verification to always fail with a "mock" error.
        "mockerror": None,
        # Generates a “mock” challenge within the widget, bypassing the request to
        # challengeurl.
        "test": None,
    }

    def __init__(self, *args, **kwargs):
        """Initialize the ALTCHA field and pass widget options for rendering."""
        widget_options = {
            key: kwargs.pop(key, self.default_options[key])
            for key in self.default_options
        }
        kwargs["widget"] = self.widget(options=widget_options)
        super().__init__(*args, **kwargs)

    def validate(self, value):
        """Validate the CAPTCHA token and verify its authenticity."""
        if not ALTCHA_VERIFICATION_ENABLED:
            return

        super().validate(value)

        if not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )

        try:
            verified, error = altcha.verify_solution(
                payload=value,
                hmac_key=ALTCHA_HMAC_KEY,
                check_expires=True,
            )
        except Exception:
            raise forms.ValidationError(self.error_messages["error"], code="error")

        if not verified:
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

        self.replay_attack_protection(payload=value)

    def replay_attack_protection(self, payload):
        """Protect against replay attacks by ensuring each challenge is single-use."""
        try:
            # Decode payload from base64 and parse JSON to extract the challenge
            payload_data = json.loads(base64.b64decode(payload).decode())
            challenge = payload_data["challenge"]
        except Exception:
            raise forms.ValidationError(self.error_messages["error"], code="error")

        if is_challenge_used(challenge):
            raise forms.ValidationError(self.error_messages["replay"], code="invalid")

        # Mark as used for the same duration as challenge expiration
        mark_challenge_used(challenge, timeout=ALTCHA_CHALLENGE_EXPIRE_SECONDS)


class AltchaChallengeView(View):
    max_number = None
    expires = None

    @method_decorator(require_GET)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Use view's class attributes or kwargs
        max_number = kwargs.get("max_number", self.max_number)
        expires = kwargs.get("expires", self.expires)

        challenge = get_altcha_challenge(max_number=max_number, expires=expires)
        return JsonResponse(challenge.__dict__)

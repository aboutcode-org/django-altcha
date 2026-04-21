#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import base64
import datetime
import json
import logging

from django import forms
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import HiddenInput
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_GET

import altcha

from .conf import get_setting

__version__ = "0.10.0"
VERSION = __version__

logger = logging.getLogger(__name__)


def get_hmac_key():
    """Return the HMAC key, raising if not configured."""
    hmac_key = get_setting("ALTCHA_HMAC_KEY")
    if not hmac_key:
        logger.error("ALTCHA_HMAC_KEY setting is not configured")
        raise ImproperlyConfigured("The ALTCHA_HMAC_KEY setting must be provided.")
    return hmac_key


def get_challenge_expire_seconds():
    return get_setting("ALTCHA_CHALLENGE_EXPIRE") // 1000


def get_cache():
    """Return the cache backend used for replay attack protection."""
    return caches[get_setting("ALTCHA_CACHE_ALIAS")]


def is_challenge_used(challenge):
    """Check if a challenge has already been used."""
    return get_cache().get(key=challenge) is not None


def mark_challenge_used(challenge, timeout):
    """Mark a challenge as used by storing it in the cache with a timeout."""
    get_cache().set(key=challenge, value=True, timeout=timeout)


def get_altcha_challenge(max_number=None, expires=None):
    """
    Generate and return an ALTCHA challenge.

    Attributes:
        max_number (int): Maximum number to use for the challenge.
        expires (int): Expiration time for the challenge in milliseconds.

    Returns:
        altcha.Challenge: The generated challenge.
    """
    expires = expires or get_setting("ALTCHA_CHALLENGE_EXPIRE")
    options = {
        "hmac_key": get_hmac_key(),
        "expires": datetime.datetime.now() + datetime.timedelta(milliseconds=expires),
    }

    if max_number is not None:
        options["max_number"] = max_number

    challenge = altcha.create_challenge(altcha.ChallengeOptions(**options))
    return challenge


class AltchaWidget(HiddenInput):
    template_name = "altcha_widget.html"

    def __init__(self, options=None, *args, **kwargs):
        """Initialize the ALTCHA widget with provided options from the field."""
        self.options = options or {}
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        """Generate the widget context, including ALTCHA JS URL and challenge."""
        context = super().get_context(name, value, attrs)
        context["js_altcha_url"] = get_setting("ALTCHA_JS_URL")
        context["js_translations_url"] = get_setting("ALTCHA_JS_TRANSLATIONS_URL")
        context["include_translations"] = get_setting("ALTCHA_INCLUDE_TRANSLATIONS")

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
        "expire": None,
        # Enable floating UI.
        # Possible values: "auto", "top", "bottom".
        "floating": None,
        # CSS selector of the "anchor" to which the floating UI is attached.
        # Default: submit button in the related form.
        "floatinganchor": None,
        # Y offset from the anchor element for the floating UI (in pixels, default: 12).
        "floatingoffset": None,
        # Enable a "persistent" mode to keep the widget visible under specific
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
        # Generates a "mock" challenge within the widget, bypassing the request to
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
        if not get_setting("ALTCHA_VERIFICATION_ENABLED"):
            logger.debug(
                "ALTCHA validation skipped: ALTCHA_VERIFICATION_ENABLED is False"
            )
            return

        super().validate(value)

        if not value:
            logger.warning("ALTCHA validation failed: missing token")
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )

        try:
            verified, error = altcha.verify_solution(
                payload=value,
                hmac_key=get_hmac_key(),
                check_expires=True,
            )
        except Exception:
            logger.exception("ALTCHA validation raised an unexpected exception")
            raise forms.ValidationError(self.error_messages["error"], code="error")

        if not verified:
            logger.warning("ALTCHA validation failed: %s", error)
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

        self.replay_attack_protection(payload=value)

    def replay_attack_protection(self, payload):
        """Protect against replay attacks by ensuring each challenge is single-use."""
        try:
            # Decode payload from base64 and parse JSON to extract the challenge
            payload_data = json.loads(base64.b64decode(payload).decode())
            challenge = payload_data["challenge"]
        except Exception:
            logger.exception(
                "ALTCHA payload could not be decoded for replay protection"
            )
            raise forms.ValidationError(self.error_messages["error"], code="error")

        if is_challenge_used(challenge):
            logger.warning("ALTCHA replay attack detected: challenge already used")
            raise forms.ValidationError(self.error_messages["replay"], code="invalid")

        # Mark as used for the same duration as challenge expiration
        mark_challenge_used(challenge, timeout=get_challenge_expire_seconds())


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
        logger.debug("ALTCHA challenge issued")
        return JsonResponse(challenge.__dict__)

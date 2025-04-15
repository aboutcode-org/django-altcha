#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import json
import secrets

import altcha
from django import forms
from django.conf import settings
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

__version__ = "0.1.2"
VERSION = __version__

# Get the ALTCHA_HMAC_KEY from the settings, or generate one if not present.
ALTCHA_HMAC_KEY = getattr(settings, "ALTCHA_HMAC_KEY", secrets.token_hex(32))
ALTCHA_JS_URL = getattr(settings, "ALTCHA_JS_URL", "/static/altcha/altcha.min.js")


def get_altcha_challenge(max_number=None):
    """Generate and return an ALTCHA challenge."""
    options = {
        "hmac_key": ALTCHA_HMAC_KEY,
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

        # If a `challengeurl` is provided, the challenge will be fetched from this URL.
        # This can be a local Django view or an external API endpoint.
        # If not provided, a unique challenge is generated locally in a self-hosted
        # mode.
        # Since the challenge must be fresh for each form rendering, it is generated
        # inside `get_context`, not `__init__`.
        if not self.options.get("challengeurl"):
            challenge = get_altcha_challenge(max_number=self.options.get("maxnumber"))
            self.options["challengejson"] = json.dumps(challenge.__dict__)

        context["widget"]["altcha_options"] = self.options
        return context


class AltchaField(forms.Field):
    widget = AltchaWidget
    default_error_messages = {
        "error": _("Failed to process CAPTCHA token"),
        "invalid": _("Invalid CAPTCHA token."),
        "required": _("ALTCHA CAPTCHA token is missing."),
    }
    default_options = {
        # URL of your server to fetch the challenge from.
        "challengeurl": None,
        # JSON-encoded challenge data
        # (use instead of challengeurl to avoid HTTP request).
        "challengejson": None,
        # Automatically verify without user interaction.
        # Possible values: "off", "onfocus", "onload", "onsubmit".
        "auto": None,
        # Artificial delay before verification (in milliseconds, default: 0).
        "delay": None,
        # Challenge expiration duration (in milliseconds).
        "expire": None,
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
        # Possible values: "true", "focus".
        "floatingpersist": None,
        # Hide the footer (ALTCHA link).
        "hidefooter": None,
        # Hide the ALTCHA logo.
        "hidelogo": None,
        # Max number to iterate to (default: 1,000,000).
        "maxnumber": None,
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
        super().validate(value)

        if not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )

        try:
            verified, error = altcha.verify_solution(
                payload=value,
                hmac_key=ALTCHA_HMAC_KEY,
                check_expires=False,
            )
        except Exception:
            raise forms.ValidationError(self.error_messages["error"], code="error")

        if not verified:
            raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

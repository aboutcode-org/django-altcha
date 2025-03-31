#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import json

from django.test import TestCase

from django_altcha import AltchaWidget


class AltchaWidgetTest(TestCase):
    def test_widget_initialization_with_default_options(self):
        widget = AltchaWidget(options=None)
        self.assertNotIn("challengeurl", widget.options)
        self.assertNotIn("challengejson", widget.options)
        self.assertNotIn("auto", widget.options)

    def test_widget_initialization_with_custom_options(self):
        options = {
            "auto": "onload",
            "delay": 500,
        }
        widget = AltchaWidget(options)
        self.assertEqual(widget.options["auto"], "onload")
        self.assertEqual(widget.options["delay"], 500)

    def test_widget_generates_challengejson_if_no_challengeurl(self):
        widget = AltchaWidget(options={})  # Pass an empty dictionary
        context = widget.get_context(name="test", value=None, attrs={})

        challengejson = json.loads(context["widget"]["altcha_options"]["challengejson"])
        self.assertEqual("SHA-256", challengejson["algorithm"])
        self.assertEqual(64, len(challengejson["challenge"]))

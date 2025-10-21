#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import json

from django.test import TestCase

from django_altcha import AltchaWidget


class DjangoAltchaWidgetTest(TestCase):
    def test_widget_initialization_with_default_options(self):
        widget = AltchaWidget(options=None)
        self.assertNotIn("challengeurl", widget.options)
        self.assertNotIn("challengejson", widget.options)
        self.assertNotIn("auto", widget.options)

    def test_widget_initialization_with_custom_options(self):
        options = {
            "auto": "onload",
            "delay": 500,
            "expire": 100000,
        }
        widget = AltchaWidget(options)
        self.assertEqual(widget.options["auto"], "onload")
        self.assertEqual(widget.options["delay"], 500)
        self.assertEqual(widget.options["expire"], 100000)

    def test_widget_generates_challengejson_if_no_challengeurl(self):
        widget = AltchaWidget(options={})  # Pass an empty dictionary
        context = widget.get_context(name="test", value=None, attrs={})
        altcha_options = context["widget"]["altcha_options"]
        challengejson = json.loads(altcha_options["challengejson"])
        self.assertEqual("SHA-256", challengejson["algorithm"])
        self.assertEqual(64, len(challengejson["challenge"]))
        self.assertIn("?expires=", challengejson.get("salt"))

    def test_widget_rendering_with_complex_options(self):
        options = {
            "strings": {
                "label": "Label",
                "verified": "Verified",
            }
        }
        widget = AltchaWidget(options)
        rendered_widget_html = widget.render("name", "value")
        expected = (
            'strings="{&quot;label&quot;: &quot;Label&quot;, '
            '&quot;verified&quot;: &quot;Verified&quot;}"'
        )
        self.assertIn(expected, rendered_widget_html)

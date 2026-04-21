#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

import json

from django.test import TestCase
from django.test import override_settings

from django_altcha import AltchaWidget


class DjangoAltchaWidgetTest(TestCase):
    def test_widget_initialization_with_default_options(self):
        widget = AltchaWidget()
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

    def test_js_translation_included_if_enabled(self):
        widget = AltchaWidget()
        expected_js = "/static/altcha/dist_i18n/all.min.js"

        with override_settings(ALTCHA_INCLUDE_TRANSLATIONS=True):
            rendered_widget_html = widget.render("name", "value")
            self.assertIn(expected_js, rendered_widget_html)

        with override_settings(ALTCHA_INCLUDE_TRANSLATIONS=False):
            rendered_widget_html = widget.render("name", "value")
            self.assertNotIn(expected_js, rendered_widget_html)

    def test_widget_renders_default_js_url_through_static(self):
        widget = AltchaWidget()
        rendered_html = widget.render("name", "value")
        self.assertIn("/static/altcha/altcha.min.js", rendered_html)

    def test_widget_respects_custom_static_url(self):
        widget = AltchaWidget()
        with override_settings(STATIC_URL="/assets/"):
            rendered_html = widget.render("name", "value")
        self.assertIn("/assets/altcha/altcha.min.js", rendered_html)
        self.assertNotIn("/static/altcha/altcha.min.js", rendered_html)

    def test_widget_resolves_relative_js_url_override(self):
        widget = AltchaWidget()
        with override_settings(ALTCHA_JS_URL="custom/altcha.js"):
            rendered_html = widget.render("name", "value")
        self.assertIn("/static/custom/altcha.js", rendered_html)

    def test_widget_passes_through_absolute_js_url(self):
        widget = AltchaWidget()
        with override_settings(ALTCHA_JS_URL="/my_static/altcha.js"):
            rendered_html = widget.render("name", "value")
        self.assertIn('src="/my_static/altcha.js"', rendered_html)
        self.assertNotIn("/static/my_static/altcha.js", rendered_html)

    def test_widget_passes_through_http_js_url(self):
        widget = AltchaWidget()
        cdn_url = "http://cdn/altcha.min.js"
        with override_settings(ALTCHA_JS_URL=cdn_url):
            rendered_html = widget.render("name", "value")
        self.assertIn(cdn_url, rendered_html)

    def test_widget_passes_through_https_js_url(self):
        widget = AltchaWidget()
        cdn_url = "https://cdn/altcha.min.js"
        with override_settings(ALTCHA_JS_URL=cdn_url):
            rendered_html = widget.render("name", "value")
        self.assertIn(cdn_url, rendered_html)

    def test_widget_resolves_translations_url_through_static(self):
        widget = AltchaWidget()
        with override_settings(
            ALTCHA_INCLUDE_TRANSLATIONS=True,
            STATIC_URL="/assets/",
        ):
            rendered_html = widget.render("name", "value")
        self.assertIn("/assets/altcha/dist_i18n/all.min.js", rendered_html)

    def test_widget_passes_through_absolute_translations_url(self):
        widget = AltchaWidget()
        cdn_url = "https://cdni18n/all.min.js"
        with override_settings(
            ALTCHA_INCLUDE_TRANSLATIONS=True,
            ALTCHA_JS_TRANSLATIONS_URL=cdn_url,
        ):
            rendered_html = widget.render("name", "value")
        self.assertIn(cdn_url, rendered_html)

#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

from django.urls import path

from django_altcha import AltchaChallengeView

urlpatterns = [
    path(
        "altcha/challenge/",
        AltchaChallengeView.as_view(max_number=100),
        name="altcha_challenge",
    ),
]
